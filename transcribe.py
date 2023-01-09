from itertools import chain
import json
from stable_whisper import load_model, to_srt, transcribe_word_level, finalize_segment_word_ts
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

def finalize_results(results):
    # Get start and end timestamps for each word
    results = finalize_segment_word_ts(results)
    # Move timestamps to text objects
    results = [dict(text=j[0], **j[1]) for j in chain.from_iterable(zip(*i) for i in results)]
    # Round timestamps to 3 decimal places
    results = [dict(text=j['text'], start=round(j['start'], 3), end=round(j['end'], 3)) for j in results]

    return results

def make_words_whole(results):
    """Sticks whole words together"""
    new_results = []
    for i in results:
        if not i['text'].startswith(' '):
            new_results[-1]['text'] += i['text']
            new_results[-1]['end'] = i['end']
        else:
            new_results.append(i)
    
    return new_results

def split_into_words(results):
    """Split on spaces, then linearly interpolate the timestamps for each word using the length of the word."""
    new_results = []
    for i in results:
        words = i['text'].split()
        for j in range(len(words)):
            word = words[j]
            start = i['start'] + (i['end'] - i['start']) * sum(len(k) for k in words[:j]) / len(i['text'])
            end = i['start'] + (i['end'] - i['start']) * sum(len(k) for k in words[:j + 1]) / len(i['text'])
            new_results.append(dict(text=word, start=start, end=end))
    
    return new_results

def combine_to_segments(results, time_threshold=1, max_length=20):
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
            current_text += " " + i['text']
    
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
    # TODO: cache Whisper output?
    # TODO: more config options: model, threshold, max_length
    
    # Convert format and combine words
    with console.status(f"Finalizing Whisper results...", spinner="arc", spinner_style="blue"):
        # Format
        results = finalize_results(results)
        
        # # Print temporary results
        # for i in results:
        #     print(f"[{i['start']:0.2f} - {i['end']:0.2f}] {i['text']}")
        
        # Post processing
        results = make_words_whole(results)
        results = split_into_words(results)
        results = combine_to_segments(results, time_threshold=1)
        
        srt_filepath = filepath + '.srt'
        to_srt(results, srt_filepath)
    
    # Print results
    for i in results:
        print(f"[{i['start']:0.2f} - {i['end']:0.2f}] {i['text']}")

    log.success(f"Succesfully transcribed audio!")

    return srt_filepath
