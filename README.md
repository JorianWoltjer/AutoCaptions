# AutoCaptions

**Transcribe an audio file to Premiere Pro layers**

A GUI tool that uses [OpenAI's Whisper](https://github.com/openai/whisper) to transcribe text from an audio/video file, into a Premiere Pro sequence to automate the creation of subtitles. Mainly for adding quick subtitles to action-packed video's, by making segments of a small word count. 

Outputs a `.xml` file which is a sequence containing text layers (Essential Graphics) that can be imported into your Premiere Pro project. 

## Installation

```cmd
git clone https://github.com/JorianWoltjer/AutoCaptions.git && cd AutoCaptions
python -m pip install -r requirements.txt
```

> **Warning**: The installation is not thoroughly tested, so let me know if any problems arise by creating an [Issue](https://github.com/JorianWoltjer/AutoCaptions/issues) for example. 

### Torch

Make sure to install the GPU enabled version of `torch` to make Whisper a lot faster:

```shell
python -m pip uninstall torch
python -m pip cache purge
python -m pip install torch -f https://download.pytorch.org/whl/torch_stable.html
```

### ffmpeg

An external dependency for Whisper that needs to be installed:

###### Windows

Install [Chocolatey](https://docs.chocolatey.org/en-us/choco/setup), then run the following command:

```cmd
choco install ffmpeg
```

###### Linux

```Shell
sudo apt update && sudo apt install ffmpeg
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
