# Transcribe audio to Premiere Pro

A GUI tool that uses [OpenAI's Whisper](https://github.com/openai/whisper) to transcribe text from an audio/video file, into a Premiere Pro sequence to automate the creation of subtitles. 

Outputs a `.xml` file which is a sequence containing text layers (Essential Graphics) that can be imported into your Premiere Pro project. 

## Installation

```cmd
git clone https://github.com/JorianWoltjer/transcribe-to-premiere.git && cd transcribe-to-premiere
pip install -r requirements.txt
```

> **Warning**: The installation is not thoroughly tested, so let me know if any problems arise by creating an [Issue](https://github.com/JorianWoltjer/transcribe-to-premiere/issues) for example. 

### Torch

Make sure to install the GPU enabled version of `torch` to make Whisper faster:

```shell
pip uninstall torch
pip cache purge
pip install torch -f https://download.pytorch.org/whl/torch_stable.html
```

### ffmpeg

An external dependency for Whisper that needs to be installed:

```shell
# on Windows using Chocolatey (https://chocolatey.org/)
choco install ffmpeg

# on Windows using Scoop (https://scoop.sh/)
scoop install ffmpeg

# on Ubuntu or Debian
sudo apt update && sudo apt install ffmpeg

# on Arch Linux
sudo pacman -S ffmpeg

# on MacOS using Homebrew (https://brew.sh/)
brew install ffmpeg
```

## Running

###### Windows

Simply create a shortcut to [`start.bat`](start.bat)

###### Linux

```shell
$ python3 main.py
```

## Example

Start the batch script, and select a file as input:

![A terminal showing Whisper output and some progress updates, with the simple GUI on Windows](img/terminal_example.png)

The resulting XML file can then be imported into a Premiere project, where you can use and edit the text layers it created:

![A screenshot of the Premiere Pro timeline showing 3 text layers with the transcribed text](img/premiere_example.png)

## Resources

* https://github.com/jianfch/stable-ts
* https://github.com/openai/whisper/discussions/3#discussioncomment-3730914
