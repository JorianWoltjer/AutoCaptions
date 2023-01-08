from itertools import chain
from stable_whisper import load_model, finalize_segment_word_ts, to_srt
from log import log, console

# print(f"{results=}")

def finalize_results(results):
    # Get start and end timestamps for each word
    results = finalize_segment_word_ts(results)
    # Move timestamps to text objects
    results = [dict(text=j[0], **j[1]) for j in chain.from_iterable(zip(*i) for i in results)]
    # Round timestamps to 3 decimal places
    results = [dict(text=j['text'], start=round(j['start'], 3), end=round(j['end'], 3)) for j in results]
    
    return results

def combine_words(results, threshold=1):
    """Combine some word that are close to each other, to form small phrases.

    Basically records audio for 1 second, and combine all words in that second. The last word might overflow a bit, 
    but then we start the new second of recording at the end of the previous word.
    """
    new_results = []
    current_start = results[0]['start']
    current_end = results[0]['end']
    current_text = results[0]['text']
    for i in results[1:]:
        if i['start'] - current_start < threshold:
            # Combine words that are close to each other
            current_end = i['end']
            current_text += i['text']
        else:
            # If the current word is too far away from the previous word, we start a new phrase
            new_results.append(dict(start=current_start, end=current_end, text=current_text))
            current_start = i['start']
            current_end = i['end']
            current_text = i['text'].lstrip()
    
    new_results.append(dict(start=current_start, end=current_end, text=current_text))
    
    return new_results

# Convert audio to SRT using Whisper
def transcribe_to_srt(filepath):
    # Load model
    with console.status(f"Loading Whisper 'small' model...", spinner="arc", spinner_style="blue"):
        model = load_model('small')
    log.success("Loaded Whisper model")
    # Start transcribing
    with console.status(f"Transcribing using Whisper (this may take some time)...", spinner="arc", spinner_style="blue"):
        results = model.transcribe(filepath)
    log.success("Completed Whisper")
    
    # Convert format and combine words
    with console.status(f"Finalizing Whisper results...", spinner="arc", spinner_style="blue"):
        results = finalize_results(results)

        results = combine_words(results, threshold=1)
        
        srt_filepath = filepath + '.srt'
        to_srt(results, srt_filepath)
    
    # Print results
    for i in results:
        print(f"[{i['start']:>5.2f} - {i['end']:>5.2f}] {i['text']}")

    log.success(f"Succesfully transcribed audio!")

    return srt_filepath
