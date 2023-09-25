from hashlib import md5
import os, sys
import torch, gc
import json
from stable_whisper import load_faster_whisper, WhisperResult
from log import log, console

DIR = sys.path[0]

def unique_filename(filepath, model_name):
    hash = md5(open(filepath, 'rb').read()).hexdigest()
    path = os.path.join(DIR, 'cache', f"{hash}-{model_name}.json")
    return path

def get_cache(filepath, model_name) -> WhisperResult:
    """Check if the Whisper output is cached, and if so, return it."""
    filepath = unique_filename(filepath, model_name)
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            return WhisperResult(json.load(f))

def put_cache(filepath, model_name, results: WhisperResult):
    """Cache the Whisper output."""
    os.makedirs(os.path.join(DIR, 'cache'), exist_ok=True)
    filepath = unique_filename(filepath, model_name)
    with open(filepath, 'w') as f:
        json.dump(results.to_dict(), f)

# Convert audio to SRT using Whisper
def transcribe_to_srt(filepath, model_name='small', split_gap=0.5, split_length=20):
    cached = get_cache(filepath, model_name)
    if cached:
        result = cached
        log.success("Loaded [green]CACHED[/green] Whisper results!")
    else:
        # Load model
        log.progress(f"Loading Whisper {model_name!r} model...")
        model = load_faster_whisper(model_name)
        log.success("Loaded Whisper model")
        # Start transcribing
        log.progress(f"Transcribing using Whisper (this may take some time)...")
        # result: WhisperResult = model.transcribe(filepath, regroup=False)
        result: WhisperResult = model.transcribe_stable(filepath, regroup=False)
        
        put_cache(filepath, model_name, result)
        log.success("Completed Whisper (and saved to cache)")
    
    # Convert format and combine words
    with console.status(f"Regrouping words...", spinner="arc", spinner_style="blue"):
        (  # Thanks stable-ts for a better implementation of what I did myself :)
            result
            .clamp_max()
            .split_by_punctuation([('.', ' '), '。', '?', '？', (',', ' '), '，'])  # Use nice split places
            .split_by_gap(split_gap)  # Split gaps of >0.3 seconds
            .split_by_length(split_length)  # Max length of 20 characters
            .split_by_punctuation([('.', ' '), '。', '?', '？'])  # Force split by punctuation
        )
        
        srt_filepath = filepath + '.srt'
        result.to_srt_vtt(srt_filepath, word_level=False)
        # TODO: In the future maybe add word-level animation?
    
    # Print results
    for seg in result.to_dict()['segments']:
        print(f"[{seg['start']:0.2f} - {seg['end']:0.2f}]  {seg['text'].strip()}")

    log.success(f"Succesfully transcribed audio!")
    
    # Prevent memory leak
    if not cached:
        del model
        gc.collect()
        torch.cuda.empty_cache()
        if torch.cuda.memory_allocated() > 0:
            log.warning("[yellow]WARNING[/yellow]: Memory was not fully cleared. This is a bug! Please report it with some information about your system.")

    return srt_filepath
