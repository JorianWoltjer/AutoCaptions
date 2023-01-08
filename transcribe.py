from itertools import chain
import json
from stable_whisper import load_model, to_srt, transcribe_word_level
from log import log, console

def add_start_end_times(results):
    # Add last word, one second later
    results += [{'word': '', 'timestamp': results[-1]['timestamp'] + 1}]
    
    new_results = []
    for i in range(len(results) - 1):
        item = {
            'text': results[i]['word'],
            'start': results[i]['timestamp'],
            'end': results[i + 1]['timestamp'],
        }
        new_results.append(item)

    return new_results

def make_whole_words(results):
    """Sticks whole words together"""
    new_results = []
    for i in results:
        if not i['text'].startswith(' '):
            new_results[-1]['text'] += i['text']
            new_results[-1]['end'] = i['end']
        else:
            new_results.append(i)
    
    return new_results

def combine_close_words(results, time_threshold=1, max_length=20):
    """Combine some word that are close to each other, to form small phrases.

    Basically records audio for 1 second, and combine all words in that second. The last word might overflow a bit, 
    but then we start the new second of recording at the end of the previous word.
    """
    new_results = []
    current_start = results[0]['start']
    current_end = results[0]['end']
    current_text = results[0]['text']
    for i in results[1:]:
        # If the current word is too far away from the previous word, we start a new phrase
        # If the previous word ends with a punctuation mark, we start a new phrase
        # If the previous phrase is too long, we start a new phrase
        if i['start'] - current_start > time_threshold or \
                current_text[-1] in '.?!' or \
                len(current_text + i['text']) > max_length:
            # If the current word is too far away from the previous word, we start a new phrase
            new_results.append(dict(start=current_start, end=current_end, text=current_text))
            current_start = i['start']
            current_end = i['end']
            current_text = i['text'].lstrip()
        else:
            # Combine words that are close to each other
            current_end = i['end']
            current_text += i['text']
    
    new_results.append(dict(start=current_start, end=current_end, text=current_text))
    
    return new_results

# Convert audio to SRT using Whisper
def transcribe_to_srt(filepath):
    # Load model
    with console.status(f"Loading Whisper 'small' model...", spinner="arc", spinner_style="blue"):
        model = load_model('small')
    log.success("Loaded Whisper model")
    # Start transcribing
    log.progress(f"Transcribing using Whisper (this may take some time)...")
    
    results = transcribe_word_level(model, filepath, pbar=True)
    log.success("Completed Whisper")
    
    # Convert format and combine words
    with console.status(f"Finalizing Whisper results...", spinner="arc", spinner_style="blue"):
        # Format
        results = list(chain(*[segment["word_timestamps"] for segment in results["segments"]]))
        results = add_start_end_times(results)
        
        # # Print temporary results
        # for i in results:
        #     print(f"[{i['start']:0.2f} - {i['end']:0.2f}] {i['text']}")
        
        # Post processing
        results = make_whole_words(results)
        results = combine_close_words(results, time_threshold=0.5)
        
        srt_filepath = filepath + '.srt'
        to_srt(results, srt_filepath)
    
    # Print results
    for i in results:
        print(f"[{i['start']:0.2f} - {i['end']:0.2f}] {i['text']}")

    log.success(f"Succesfully transcribed audio!")

    return srt_filepath
