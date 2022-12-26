import tkinter as tk
import tkinter.ttk as ttk
from tkinter import ACTIVE, DISABLED, filedialog
from pathlib import Path
import os
import subprocess
import sys

sys.path.append(os.path.dirname(os.path.realpath(__file__)))  # Allow local imports from any working directory
from log import console, log
import premiere_convert

DIR = sys.path[0]

# GUI

root = tk.Tk()
root.geometry('370x150')
root.title('Transcribe Audio to Premiere Pro XML')

def select_file():
    filetypes = [
        ("Audio Files", "*.wav;*.mp3;*.flac;*.aac;*.m4a"),
        ("Video Files", "*.mp4;*.mov*;.avi;*.mkv;*.wmv"),
        ('All files', '*.*')
    ]

    filename_ask = filedialog.askopenfilename(
        title='Select any Audio or Video file to be transcribed',
        initialdir='/',
        filetypes=filetypes)
    
    if filename_ask == "":  # if dialog closed with cancel
        return
    
    text_label.set(filename_ask)
    convert_button["state"] = ACTIVE

def file_save():
    filetypes = (
        ('Premiere Pro Sequence file', '*.xml'),
        ('All files', '*.*')
    )
    
    path = Path(text_label.get())
    directory = path.parent
    filename = path.stem + ".xml"
    
    f = filedialog.asksaveasfile(mode='w', title="Save sequence file", filetypes=filetypes, initialdir=directory, initialfile=filename)
    f.close()
    if f is None:  # if dialog closed with cancel
        return
    
    input_filepath = text_label.get()
    
    convert_button["state"] = DISABLED
    text_label.set("Transcribing... (see console for progress)")
    root.update()

    # Transcribe audio using Whisper
    srt_filepath = transcribe(input_filepath)
    
    # Convert SRT to Premiere XML text layers
    srt_to_xml(srt_filepath, f.name)
    
    # Open file in Explorer
    if sys.platform == "win32":
        open_file_in_explorer(f)

    root.destroy()

# Convert audio to SRT using Whisper
def transcribe(filepath):
    dirname = os.path.dirname(filepath)

    log.info(f"Starting Whisper... (into {dirname})")

    return_code = subprocess.call(["python", "-m", "whisper", filepath, "-o", dirname], cwd=DIR)

    if return_code == 0:
        srt_filepath = os.path.join(dirname, os.path.basename(filepath) + ".srt")
        log.success(f"Succesfully transcribed audio! Saved to {srt_filepath}")
    else:
        log.error(f"ERROR: Whisper failed with return code {return_code}.")
    
    return srt_filepath


# Convert SRT to Premiere Pro XML Sequence as Text Layers
def srt_to_xml(srt_filename, outfile):
    with console.status(f"Converting {srt_filename} to Premiere Pro XML...", spinner="arc", spinner_style="blue"):
        premiere_xml = premiere_convert.srt_to_xml(srt_filename)

        # Write to file
        outfile = outfile + ".xml" if not outfile.endswith(".xml") else outfile

        with open(outfile, "w") as f:
            f.write(premiere_xml)
    
    log.success(f"Saved Premiere Pro XML to {outfile}")

def open_file_in_explorer(f):
    filename = f.name.replace('/', '\\')
    subprocess.Popen(f'explorer /select,"{filename}"')


# Setup GUI
ttk.Label(text="Input Audio file").pack(anchor="center", pady=(15, 0))
ttk.Button(text='Browse', command=select_file).pack(ipadx=30)
text_label = tk.StringVar()
ttk.Label(textvariable=text_label).pack(anchor="center", pady=(15, 0))
convert_button = ttk.Button(text='Transcribe to XML', command=file_save, state=DISABLED)
convert_button.pack(pady=15)

log.info("Starting GUI")
root.mainloop()
