╔══════════════════════════════════════════════════════════════════════╗
║                    AI VIDEO STUDIO PRO v5.0                          ║
║              Professional Desktop Video Editor                        ║
╚══════════════════════════════════════════════════════════════════════╝

THIS IS A PROFESSIONAL GUI APPLICATION - NOT COMMAND LINE!

FEATURES:
=========

1. PROFESSIONAL GUI INTERFACE
   - Modern dark theme
   - Easy to use controls
   - Preview panel
   - Timeline view
   - Progress logging

2. KEN BURNS EFFECT (SLOW ZOOM)
   - Automatic slow zoom on images
   - Adjustable zoom intensity (1.0x - 1.5x)
   - Creates cinematic movement

3. FADE TRANSITIONS
   - Smooth crossfade between images
   - Adjustable transition duration
   - Professional look

4. BACKGROUND MUSIC SUPPORT
   - Add background music to video
   - Mixes with narration

5. OVERLAY / WATERMARK
   - Add logo or watermark
   - Positioned in corner
   - Semi-transparent

6. INTELLIGENT SYNC
   - AI analyzes audio word-by-word
   - AI understands each image content
   - Automatically matches images to narration


INSTALLATION:
=============

Step 1: Install Python 3.8+
---------------------------
Download from: https://python.org
IMPORTANT: Check "Add Python to PATH" during installation!

Step 2: Install Dependencies
----------------------------
Open Command Prompt and run:

    pip install requests Pillow

Step 3: Install FFmpeg
----------------------
Windows:
  1. Download from: https://www.gyan.dev/ffmpeg/builds/
  2. Download "ffmpeg-release-essentials.zip"
  3. Extract to C:\ffmpeg
  4. Add C:\ffmpeg\bin to System PATH:
     - Search "Environment Variables" in Windows
     - Edit PATH variable
     - Add: C:\ffmpeg\bin
  5. Restart Command Prompt

Mac:
    brew install ffmpeg

Linux:
    sudo apt install ffmpeg


RUNNING THE APP:
================

Windows:
  Double-click: start.bat
  Or run: python ai_studio_gui.py

Mac/Linux:
  Run: ./start.sh
  Or: python3 ai_studio_gui.py


HOW TO USE:
===========

1. CLICK "Select Audio File"
   - Choose your narration/voice file (MP3, WAV)

2. CLICK "Add Images Folder" or "Add Individual Images"
   - Add all your images

3. ADJUST EFFECTS:
   - Ken Burns Zoom: Enable/disable, adjust intensity
   - Fade Transitions: Enable/disable, adjust duration

4. OPTIONAL:
   - Add Overlay/Watermark image
   - Add Background Music

5. CLICK "GENERATE VIDEO"
   - Choose save location
   - Wait for processing

   OR

   CLICK "INTELLIGENT SYNC" (Requires OpenAI API)
   - AI will match images to narration automatically


SETTINGS:
=========

Click ⚙️ Settings button to:
- Add OpenAI API Key (for intelligent sync)
- Change video resolution


FOR INTELLIGENT SYNC:
=====================

You need OpenAI API Key:
1. Go to: https://platform.openai.com/api-keys
2. Create account / Login
3. Generate API key
4. Add key in Settings


TIPS:
=====

1. Use high-quality images (1920x1080 or larger)
2. Name images in order: 001.jpg, 002.jpg, etc.
3. Ken Burns effect works best with landscape images
4. For long videos, allow more processing time


TROUBLESHOOTING:
================

"FFmpeg not found":
  - Make sure FFmpeg is installed and in PATH
  - Restart your computer after installing

"Module not found":
  - Run: pip install requests Pillow

"API Error":
  - Check your OpenAI API key in Settings
  - Make sure you have API credits


Enjoy creating professional videos!
