╔══════════════════════════════════════════════════════════════════╗
║                    AI VIDEO STUDIO PRO v3.0                      ║
║              Professional Video Generator with Sync              ║
╚══════════════════════════════════════════════════════════════════╝

NEW IN v3.0 - SYNC VIDEO CREATOR:
=================================
- Upload YOUR OWN audio file (no API needed for audio)
- Upload YOUR OWN images
- Perfect word-by-word synchronization
- No time limit - supports 4-5 hours videos!
- Smart audio analysis

HOW IT WORKS:
=============
1. You provide your audio file (MP3, WAV, M4A, FLAC)
2. You provide folder with images (JPG, PNG, WEBP)
3. Tool analyzes audio to detect words/sentences
4. Each image shows during specific words
5. Creates perfectly synced video!

SUPPORTED FORMATS:
==================
Audio: MP3, WAV, M4A, FLAC, OGG
Images: JPG, PNG, WEBP, BMP, GIF
Video Output: MP4 (H.264)

INSTALLATION:
=============

Step 1: Install Python 3.8+
---------------------------
Download from: https://python.org

Step 2: Install FFmpeg
----------------------
Windows:
  1. Download from https://ffmpeg.org/download.html
  2. Extract to C:\ffmpeg
  3. Add C:\ffmpeg\bin to PATH

Mac: brew install ffmpeg
Linux: sudo apt install ffmpeg

Step 3: Install Dependencies
----------------------------
pip install requests Pillow

Optional (for Smart Sync):
pip install openai-whisper

Or use OpenAI API key for cloud transcription.

USAGE:
======

1. Run the tool:
   python ai_studio.py

2. Select [1] Sync Video Creator

3. Enter path to your audio file
   Example: C:\Users\You\audio.mp3

4. Enter path to images folder
   Example: C:\Users\You\images

5. Choose sync mode:
   - Smart Sync (needs OpenAI API or local Whisper)
   - Even Distribution (no API needed)

6. Wait for video creation!

API KEYS (Optional):
====================
For additional features:

- OpenAI API (Smart Sync): https://platform.openai.com/api-keys
- ElevenLabs (AI Voice): https://elevenlabs.io
- Ideogram (AI Images): https://ideogram.ai/api

TIPS:
=====
1. Name your images in order: 001.jpg, 002.jpg, 003.jpg...
2. For best sync, use clear audio without background music
3. More images = more frequent transitions
4. Use high resolution images (1920x1080 or higher)

FOLDER STRUCTURE:
=================
pro_tool_v3/
├── ai_studio.py      (main program)
├── config.json       (settings)
├── requirements.txt  (dependencies)
├── README.txt        (this file)
├── start.bat         (Windows launcher)
├── start.sh          (Mac/Linux launcher)
└── projects/         (your created videos)

Enjoy creating videos!
