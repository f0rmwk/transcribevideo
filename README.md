# transcribevideo
Transcribe Speech from Audio &amp; Video using Whisper
Requirements:

If FFmpeg is not installed then <b>ffmpeg.exe must be in the same folder as transcribevideo.</b>

Supported File Formats
You can transcribe the following file types:

Video: .mp4, .mov, .mkv, .avi
Audio: .mp3, .wav, .flac, .aac, .m4a

How to build a standalone .EXE from transcodevideo.py
-----------------------------------------------------

1) Create and Activate a Python Virtual Environment
   ```
   cd "C:\path\to\project"
   python -m venv venv
   .\venv\Scripts\activate
   ```
3) Install Dependencies
   ```
   pip install torch==2.0.1+cpu torchaudio==2.0.1+cpu -f https://download.pytorch.org/whl/cpu
   pip install openai-whisper
   pip install pyinstaller
   ```
4) Confirm transcodevideo.py Works

   ```
   python .\transcodevideo.py
   ```
   
5) Place ffmpeg.exe in the same folder as transcodevideo.py

6) Find Whisper's "assets" Folder
   It is usually in:
   ```
   C:\path\to\project\venv\Lib\site-packages\whisper\assets
8) Run PyInstaller
   ```
   pyinstaller --onefile transcodevideo.py ^
       --add-data "C:\path\to\project\venv\Lib\site-packages\whisper\assets;whisper/assets" ^
       --add-binary "ffmpeg.exe;."
   ```
   Explanation:
   - --onefile : produce a single .exe
   - --add-data : bundle Whisper's "assets" folder
   - --add-binary : bundle ffmpeg.exe

f0rm - 03/19/2025

openai/whisper is licensed under the:

MIT License

Copyright (c) 2022 OpenAI

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

https://github.com/openai/whisper

### FFmpeg Licensing Information

This software includes FFmpeg, which is licensed under the **LGPL v2.1 or later**.  
The full FFmpeg license can be found in 3rd-party-licenses/FFmpeg-LICENSE.  

You can obtain the source code and more information from the official FFmpeg website:  
➡ **https://ffmpeg.org/** 
