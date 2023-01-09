import sys, os
sys.path.append(os.path.dirname(os.path.realpath(__file__)))  # Allow local imports from any working directory
from log import console, log

log.progress("Loading modules...")

import tkinter
from tkinter import ttk
from tkinter import ACTIVE, DISABLED, filedialog
import sv_ttk
from pathlib import Path
import subprocess

import premiere_convert
from transcribe import transcribe_to_srt

DIR = sys.path[0]

def select_file():
    filetypes = [
        ("Audio Files", "*.wav;*.mp3;*.flac;*.aac;*.m4a"),
        ("Video Files", "*.mp4;*.mov;*.avi;*.mkv;*.wmv"),
        ('All files', '*.*')
    ]

    filename_ask = filedialog.askopenfilename(
        title='Select any Audio or Video file to be transcribed',
        filetypes=filetypes)
    
    if filename_ask == "":  # if dialog closed with cancel
        return
    
    input_file_variable.set(filename_ask)
    feedback_variable.set("")
    start_button["state"] = ACTIVE
    start_button.focus()

def file_save():
    filetypes = (
        ('Premiere Pro Sequence file', '*.xml'),
        ('All files', '*.*')
    )
    
    path = Path(input_file_variable.get())
    directory = path.parent
    filename = path.stem + ".xml"
    
    f = filedialog.asksaveasfile(mode='w', title="Save sequence file", filetypes=filetypes, initialdir=directory, initialfile=filename)
    if f is None:  # if dialog closed with cancel
        return
    f.close()
    
    input_filepath = input_file_variable.get()
    
    start_button["state"] = DISABLED
    feedback_variable.set("Running... (see console for progress)")
    window.update()
    
    # Get configuration
    config_model = model_variable.get()
    config_max_time = float(max_time_variable.get())
    config_max_length = int(max_length_variable.get())

    # Transcribe audio using Whisper
    srt_filepath = transcribe_to_srt(input_filepath, 
                                     model_name=config_model,
                                     max_time=config_max_time,
                                     max_length=config_max_length)

    # Convert SRT to Premiere XML text layers
    outfile = srt_to_xml(srt_filepath, f.name)
    
    # Open file in Explorer
    if sys.platform == "win32":
        open_file_in_explorer(f)
        
    feedback_variable.set("Done! Saved to " + outfile)

# Convert SRT to Premiere Pro XML Sequence as Text Layers
def srt_to_xml(srt_filename, outfile):
    with console.status(f"Converting {srt_filename} to Premiere Pro XML...", spinner="arc", spinner_style="blue"):
        premiere_xml = premiere_convert.srt_to_xml(srt_filename)

        # Write to file
        outfile = outfile + ".xml" if not outfile.endswith(".xml") else outfile

        with open(outfile, "w") as f:
            f.write(premiere_xml)
    
    log.success(f"Saved Premiere Pro XML to {outfile!r}")
    return outfile

def open_file_in_explorer(f):
    filename = f.name.replace('/', '\\')
    subprocess.Popen(f'explorer /select,"{filename}"')


window = tkinter.Tk()
window.title('Transcribe Audio to Premiere Pro XML')

frame = ttk.Frame(window)
frame.pack()

input_file_button = ttk.Button(frame, text="Select input file", command=select_file)
input_file_button.grid(row=0, column=0, sticky="news", padx=20, pady=10)
input_file_button.focus()
input_file_variable = tkinter.StringVar(window)
input_file_label = ttk.Label(frame, text="No file selected", textvariable=input_file_variable)
input_file_label.grid(row=1, column=0, sticky="news", padx=20)

config_frame = ttk.LabelFrame(frame, text="Configuration")
config_frame.grid(row=2, column=0, padx=20, pady=10)

model_label = ttk.Label(config_frame, text="Whisper Model")
model_label.grid(row=0, column=0)
model_variable = tkinter.StringVar(window)
model_variable.set("small")
model_combobox = ttk.Combobox(config_frame, values=["small", "medium", "large"], textvariable=model_variable)
model_combobox.grid(row=1, column=0)

max_time_label = ttk.Label(config_frame, text="Max time (s)")
max_time_label.grid(row=0, column=1)
max_time_variable = tkinter.StringVar(window)
max_time_variable.set("1.0")
max_time_spinbox = ttk.Spinbox(config_frame, from_=0, to=5, increment=0.1, textvariable=max_time_variable)
max_time_spinbox.grid(row=1, column=1)

max_length_label = ttk.Label(config_frame, text="Max characters")
max_length_label.grid(row=0, column=2)
max_length_variable = tkinter.StringVar(window)
max_length_variable.set("20")
max_length_spinbox = ttk.Spinbox(config_frame, from_=0, to=100, increment=1, textvariable=max_length_variable)
max_length_spinbox.grid(row=1, column=2)

for widget in config_frame.winfo_children():
    widget.grid_configure(padx=10, pady=10)

feedback_variable = tkinter.StringVar(window)
feedback_label = ttk.Label(frame, textvariable=feedback_variable)
feedback_label.grid(row=3, column=0, sticky="news", padx=20)
start_button = ttk.Button(frame, text="Transcribe to XML", command=file_save, state=DISABLED)
start_button.grid(row=4, column=0, sticky="news", padx=20, pady=10)

sv_ttk.set_theme("dark")

log.progress("Starting GUI")
window.mainloop()
