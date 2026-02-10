╔══════════════════════════════════════════════════════════════════╗
║                    AI VIDEO STUDIO PRO                           ║
║                  Professional Video Generator                     ║
╚══════════════════════════════════════════════════════════════════╝

FEATURES:
=========
1. Bulk Image + Voice → Video
   - Upload your images
   - Add AI voice
   - Auto-sync images with voice

2. Auto Video Generation
   - Just write script
   - AI generates images
   - AI generates voice
   - Creates video automatically

3. Audio Only
   - Generate voice from text
   - Uses ElevenLabs API
   - High quality audio

4. Image Only
   - Single image generation
   - Batch image generation
   - Uses Ideogram or Gemini

5. Project Manager
   - Save all projects
   - Easy access to files

6. Settings
   - Choose image provider
   - Video resolution
   - Output format


INSTALLATION:
=============

Step 1: Install Python
----------------------
Download from: https://python.org

Step 2: Install Dependencies
----------------------------
Open terminal/cmd and run:

    pip install requests Pillow

Step 3: Install FFmpeg
----------------------
Windows: Download from https://ffmpeg.org/download.html
         Add to PATH

Mac:     brew install ffmpeg

Linux:   sudo apt install ffmpeg


USAGE:
======

Step 1: Run the tool
--------------------
    python ai_studio.py

Step 2: Configure API Keys (Option 7)
-------------------------------------
You need:
- ElevenLabs API Key: https://elevenlabs.io
- ElevenLabs Voice ID: Get from ElevenLabs dashboard
- Ideogram API Key: https://ideogram.ai/api
- Gemini API Key: https://makersuite.google.com/app/apikey

Step 3: Start Creating!
-----------------------
Choose from menu:
[1] Bulk Image Video
[2] Auto Video
[3] Audio Only
[4] Image Only


FOLDER STRUCTURE:
=================

pro_tool/
├── ai_studio.py      (main program)
├── config.json       (settings)
├── requirements.txt  (dependencies)
├── README.txt        (this file)
├── projects/         (your projects)
└── temp/             (temporary files)


SUPPORT:
========
For issues, check:
- FFmpeg is installed correctly
- API keys are valid
- Internet connection is working


Enjoy creating videos!
