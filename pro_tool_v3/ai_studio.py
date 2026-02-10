#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════╗
║                    AI VIDEO STUDIO PRO v3.0                      ║
║              Professional Video Generator with Sync              ║
╠══════════════════════════════════════════════════════════════════╣
║  NEW: Upload your own audio + images = Perfect synced video!     ║
║  - Word-by-word audio analysis                                   ║
║  - Perfect image-voice synchronization                           ║
║  - No time limit (4-5 hours supported)                          ║
╚══════════════════════════════════════════════════════════════════╝
"""

import os
import sys
import json
import requests
import subprocess
import time
import base64
import shutil
import re
import math
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple

# ═══════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════

APP_NAME = "AI Video Studio Pro"
VERSION = "3.0.0"
CONFIG_FILE = Path(__file__).parent / "config.json"
PROJECTS_DIR = Path(__file__).parent / "projects"
TEMP_DIR = Path(__file__).parent / "temp"

DEFAULT_CONFIG = {
    "api_keys": {
        "elevenlabs": "",
        "elevenlabs_voice_id": "",
        "ideogram": "",
        "gemini": "",
        "openai": ""
    },
    "settings": {
        "image_provider": "ideogram",
        "video_resolution": "1920x1080",
        "video_fps": 30,
        "output_format": "mp4",
        "sync_mode": "sentences"
    }
}

# ═══════════════════════════════════════════════════════════════════
# UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    clear_screen()
    print(f"""{Colors.CYAN}
╔══════════════════════════════════════════════════════════════════╗
║                    {Colors.BOLD}AI VIDEO STUDIO PRO{Colors.END}{Colors.CYAN}                           ║
║                      Version {VERSION}                              ║
║           {Colors.YELLOW}Perfect Audio-Image Sync Technology{Colors.END}{Colors.CYAN}                 ║
╚══════════════════════════════════════════════════════════════════╝{Colors.END}
""")

def print_success(msg):
    print(f"{Colors.GREEN}✓ {msg}{Colors.END}")

def print_error(msg):
    print(f"{Colors.RED}✗ {msg}{Colors.END}")

def print_info(msg):
    print(f"{Colors.BLUE}ℹ {msg}{Colors.END}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠ {msg}{Colors.END}")

def progress_bar(current, total, prefix='Progress', length=40):
    percent = current / total if total > 0 else 0
    filled = int(length * percent)
    bar = '█' * filled + '░' * (length - filled)
    print(f'\r{prefix} |{bar}| {percent*100:.1f}%', end='', flush=True)
    if current == total:
        print()

def format_time(seconds):
    """Format seconds to HH:MM:SS"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"

def load_config():
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
            for key in DEFAULT_CONFIG:
                if key not in config:
                    config[key] = DEFAULT_CONFIG[key]
            return config
    return DEFAULT_CONFIG.copy()

def save_config(config):
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)

def ensure_dirs():
    PROJECTS_DIR.mkdir(parents=True, exist_ok=True)
    TEMP_DIR.mkdir(parents=True, exist_ok=True)

# ═══════════════════════════════════════════════════════════════════
# AUDIO ANALYZER - Word-by-Word Timestamps
# ═══════════════════════════════════════════════════════════════════

class AudioAnalyzer:
    """Analyze audio and extract word timestamps"""

    @staticmethod
    def get_audio_duration(audio_path: str) -> float:
        """Get audio duration in seconds"""
        cmd = [
            'ffprobe', '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            audio_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        try:
            return float(result.stdout.strip())
        except:
            return 0.0

    @staticmethod
    def transcribe_with_whisper_api(audio_path: str, api_key: str) -> Optional[Dict]:
        """Transcribe audio using OpenAI Whisper API with word timestamps"""
        url = "https://api.openai.com/v1/audio/transcriptions"

        headers = {
            "Authorization": f"Bearer {api_key}"
        }

        try:
            with open(audio_path, 'rb') as audio_file:
                files = {
                    'file': audio_file,
                    'model': (None, 'whisper-1'),
                    'response_format': (None, 'verbose_json'),
                    'timestamp_granularities[]': (None, 'word')
                }

                response = requests.post(url, headers=headers, files={
                    'file': (os.path.basename(audio_path), audio_file, 'audio/mpeg'),
                    'model': (None, 'whisper-1'),
                    'response_format': (None, 'verbose_json'),
                    'timestamp_granularities[]': (None, 'word')
                }, timeout=600)

                if response.status_code == 200:
                    return response.json()
                else:
                    print_error(f"Whisper API Error: {response.status_code}")
                    print(response.text[:500])
                    return None
        except Exception as e:
            print_error(f"Transcription error: {e}")
            return None

    @staticmethod
    def transcribe_with_local_whisper(audio_path: str) -> Optional[Dict]:
        """Transcribe using local Whisper (if installed)"""
        try:
            import whisper

            print_info("Loading Whisper model...")
            model = whisper.load_model("base")

            print_info("Transcribing audio...")
            result = model.transcribe(audio_path, word_timestamps=True)

            # Convert to standard format
            words = []
            for segment in result.get('segments', []):
                for word_info in segment.get('words', []):
                    words.append({
                        'word': word_info['word'].strip(),
                        'start': word_info['start'],
                        'end': word_info['end']
                    })

            return {
                'text': result['text'],
                'words': words
            }
        except ImportError:
            return None
        except Exception as e:
            print_error(f"Local Whisper error: {e}")
            return None

    @staticmethod
    def estimate_word_timestamps(audio_path: str, num_segments: int) -> List[Dict]:
        """Estimate timestamps by dividing audio evenly"""
        duration = AudioAnalyzer.get_audio_duration(audio_path)
        segment_duration = duration / num_segments

        timestamps = []
        for i in range(num_segments):
            timestamps.append({
                'start': i * segment_duration,
                'end': (i + 1) * segment_duration,
                'index': i
            })

        return timestamps

    @staticmethod
    def analyze_audio_segments(audio_path: str, num_images: int,
                               openai_key: str = None) -> List[Dict]:
        """
        Analyze audio and create segments for images.
        Returns list of segments with start/end times.
        """
        duration = AudioAnalyzer.get_audio_duration(audio_path)
        print_info(f"Audio duration: {format_time(duration)}")

        # Try different transcription methods
        transcription = None

        # Method 1: OpenAI Whisper API
        if openai_key and not transcription:
            print_info("Trying OpenAI Whisper API...")
            transcription = AudioAnalyzer.transcribe_with_whisper_api(audio_path, openai_key)
            if transcription:
                print_success("Transcription complete with Whisper API!")

        # Method 2: Local Whisper
        if not transcription:
            print_info("Trying local Whisper...")
            transcription = AudioAnalyzer.transcribe_with_local_whisper(audio_path)
            if transcription:
                print_success("Transcription complete with local Whisper!")

        # If transcription available, create smart segments
        if transcription and 'words' in transcription:
            words = transcription['words']
            total_words = len(words)
            words_per_image = max(1, total_words // num_images)

            segments = []
            for i in range(num_images):
                start_word_idx = i * words_per_image
                end_word_idx = min((i + 1) * words_per_image - 1, total_words - 1)

                if i == num_images - 1:
                    end_word_idx = total_words - 1

                if start_word_idx < total_words:
                    start_time = words[start_word_idx]['start']
                    end_time = words[end_word_idx]['end'] if end_word_idx < total_words else duration

                    # Get the words for this segment
                    segment_words = ' '.join([w['word'] for w in words[start_word_idx:end_word_idx+1]])

                    segments.append({
                        'index': i,
                        'start': start_time,
                        'end': end_time,
                        'duration': end_time - start_time,
                        'words': segment_words[:100] + '...' if len(segment_words) > 100 else segment_words
                    })

            return segments

        # Fallback: Even distribution
        print_warning("Using even distribution (no transcription available)")
        return AudioAnalyzer.estimate_word_timestamps(audio_path, num_images)


# ═══════════════════════════════════════════════════════════════════
# VIDEO GENERATOR - Perfect Sync
# ═══════════════════════════════════════════════════════════════════

class VideoGenerator:
    """Video generation with perfect sync"""

    @staticmethod
    def get_image_files(folder_path: str) -> List[str]:
        """Get all image files from folder, sorted"""
        valid_extensions = {'.jpg', '.jpeg', '.png', '.webp', '.bmp', '.gif'}
        images = []

        for f in sorted(os.listdir(folder_path)):
            ext = os.path.splitext(f)[1].lower()
            if ext in valid_extensions:
                images.append(os.path.join(folder_path, f))

        return images

    @staticmethod
    def create_synced_video(images: List[str], audio_path: str,
                           segments: List[Dict], output_path: str,
                           resolution: str = "1920x1080") -> bool:
        """
        Create video with perfect audio-image sync.
        Each image duration matches the audio segment.
        """
        if not images or not segments:
            print_error("No images or segments provided!")
            return False

        # Parse resolution
        width, height = map(int, resolution.split('x'))

        # Create temporary directory for processing
        temp_dir = Path(output_path).parent / "temp_frames"
        temp_dir.mkdir(exist_ok=True)

        # Create concat file with precise timing
        concat_file = Path(output_path).parent / "concat_list.txt"

        try:
            with open(concat_file, 'w') as f:
                for i, (img, seg) in enumerate(zip(images, segments)):
                    duration = seg['end'] - seg['start']
                    if duration <= 0:
                        duration = 1.0  # Minimum 1 second

                    f.write(f"file '{img}'\n")
                    f.write(f"duration {duration:.6f}\n")

                # Add last image again (FFmpeg requirement)
                f.write(f"file '{images[-1]}'\n")

            print_info("Creating video with FFmpeg...")

            # FFmpeg command for high-quality output
            cmd = [
                'ffmpeg', '-y',
                '-f', 'concat',
                '-safe', '0',
                '-i', str(concat_file),
                '-i', audio_path,
                '-vf', f'scale={width}:{height}:force_original_aspect_ratio=decrease,'
                       f'pad={width}:{height}:(ow-iw)/2:(oh-ih)/2:black,'
                       f'setsar=1',
                '-c:v', 'libx264',
                '-preset', 'medium',
                '-crf', '18',
                '-pix_fmt', 'yuv420p',
                '-c:a', 'aac',
                '-b:a', '192k',
                '-shortest',
                '-movflags', '+faststart',
                '-max_muxing_queue_size', '9999',
                output_path
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)

            # Cleanup
            concat_file.unlink(missing_ok=True)
            if temp_dir.exists():
                shutil.rmtree(temp_dir, ignore_errors=True)

            if result.returncode == 0:
                return True
            else:
                print_error(f"FFmpeg error: {result.stderr[-500:]}")
                return False

        except Exception as e:
            print_error(f"Video creation error: {e}")
            return False

    @staticmethod
    def create_long_video(images: List[str], audio_path: str,
                         output_path: str, resolution: str = "1920x1080",
                         openai_key: str = None) -> Tuple[bool, Dict]:
        """
        Create long video (any duration) with perfect sync.
        Returns (success, info_dict)
        """
        print_info(f"Processing {len(images)} images...")

        # Analyze audio
        print(f"\n{Colors.CYAN}Step 1: Analyzing audio...{Colors.END}")
        segments = AudioAnalyzer.analyze_audio_segments(
            audio_path, len(images), openai_key
        )

        if not segments:
            print_error("Failed to analyze audio!")
            return False, {}

        print_success(f"Created {len(segments)} segments")

        # Show segment preview
        print(f"\n{Colors.CYAN}Segment Preview:{Colors.END}")
        for i, seg in enumerate(segments[:5]):
            print(f"  Image {i+1}: {format_time(seg['start'])} - {format_time(seg['end'])} "
                  f"({seg['end']-seg['start']:.1f}s)")
        if len(segments) > 5:
            print(f"  ... and {len(segments)-5} more segments")

        # Create video
        print(f"\n{Colors.CYAN}Step 2: Creating video...{Colors.END}")
        success = VideoGenerator.create_synced_video(
            images, audio_path, segments, output_path, resolution
        )

        if success:
            # Get video info
            duration = AudioAnalyzer.get_audio_duration(audio_path)
            file_size = os.path.getsize(output_path) / (1024 * 1024)  # MB

            info = {
                'duration': duration,
                'duration_formatted': format_time(duration),
                'file_size_mb': file_size,
                'num_images': len(images),
                'num_segments': len(segments),
                'resolution': resolution
            }

            return True, info

        return False, {}


# ═══════════════════════════════════════════════════════════════════
# API CLASSES
# ═══════════════════════════════════════════════════════════════════

class ElevenLabsAPI:
    """ElevenLabs Text-to-Speech API"""
    BASE_URL = "https://api.elevenlabs.io/v1"

    def __init__(self, api_key: str):
        self.api_key = api_key

    def get_voices(self) -> List[Dict]:
        try:
            response = requests.get(
                f"{self.BASE_URL}/voices",
                headers={"xi-api-key": self.api_key},
                timeout=30
            )
            if response.status_code == 200:
                return response.json().get("voices", [])
        except:
            pass
        return []

    def generate_speech(self, text: str, voice_id: str, output_path: str) -> bool:
        url = f"{self.BASE_URL}/text-to-speech/{voice_id}"

        headers = {
            "Accept": "audio/mpeg",
            "xi-api-key": self.api_key,
            "Content-Type": "application/json"
        }

        data = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}
        }

        try:
            response = requests.post(url, json=data, headers=headers, timeout=300)
            if response.status_code == 200:
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                return True
        except:
            pass
        return False


class IdeogramAPI:
    """Ideogram Image Generation API"""
    BASE_URL = "https://api.ideogram.ai"

    def __init__(self, api_key: str):
        self.api_key = api_key

    def generate_image(self, prompt: str, output_path: str,
                      aspect_ratio: str = "ASPECT_16_9") -> bool:
        url = f"{self.BASE_URL}/generate"
        headers = {"Api-Key": self.api_key, "Content-Type": "application/json"}

        data = {
            "image_request": {
                "prompt": prompt,
                "aspect_ratio": aspect_ratio,
                "model": "V_2",
                "magic_prompt_option": "AUTO",
                "style_type": "REALISTIC"
            }
        }

        for attempt in range(3):
            try:
                response = requests.post(url, json=data, headers=headers, timeout=120)
                if response.status_code == 200:
                    result = response.json()
                    if 'data' in result and len(result['data']) > 0:
                        image_url = result['data'][0].get('url')
                        if image_url:
                            img_response = requests.get(image_url, timeout=60)
                            if img_response.status_code == 200:
                                with open(output_path, 'wb') as f:
                                    f.write(img_response.content)
                                return True
                time.sleep(2)
            except:
                time.sleep(2)
        return False


# ═══════════════════════════════════════════════════════════════════
# MAIN APPLICATION
# ═══════════════════════════════════════════════════════════════════

class AIVideoStudio:
    """Main Application"""

    def __init__(self):
        ensure_dirs()
        self.config = load_config()
        self.elevenlabs = None
        self.ideogram = None
        self._init_apis()

    def _init_apis(self):
        if self.config["api_keys"].get("elevenlabs"):
            self.elevenlabs = ElevenLabsAPI(self.config["api_keys"]["elevenlabs"])
        if self.config["api_keys"].get("ideogram"):
            self.ideogram = IdeogramAPI(self.config["api_keys"]["ideogram"])

    def main_menu(self):
        while True:
            print_header()
            print(f"""
{Colors.BOLD}╔════════════════════ MAIN MENU ════════════════════╗{Colors.END}
║                                                     ║
║  {Colors.CYAN}[1]{Colors.END} 🎬 {Colors.BOLD}Sync Video{Colors.END} (Your Audio + Your Images)     ║
║      {Colors.YELLOW}→ Perfect word-by-word sync!{Colors.END}                 ║
║      {Colors.YELLOW}→ No time limit (supports 4-5 hours){Colors.END}         ║
║                                                     ║
║  {Colors.CYAN}[2]{Colors.END} 🤖 Auto Video (AI Images + AI Voice)          ║
║  {Colors.CYAN}[3]{Colors.END} 🎙️  Generate Audio Only (ElevenLabs)           ║
║  {Colors.CYAN}[4]{Colors.END} 🖼️  Generate Images Only (AI)                  ║
║  {Colors.CYAN}[5]{Colors.END} 📁 Project Manager                            ║
║  {Colors.CYAN}[6]{Colors.END} ⚙️  Settings                                   ║
║  {Colors.CYAN}[7]{Colors.END} 🔑 API Configuration                          ║
║  {Colors.CYAN}[8]{Colors.END} 📖 Help                                       ║
║  {Colors.CYAN}[0]{Colors.END} 🚪 Exit                                       ║
║                                                     ║
╚═════════════════════════════════════════════════════╝
""")
            choice = input(f"{Colors.YELLOW}Enter choice: {Colors.END}").strip()

            if choice == '1':
                self.sync_video_creator()
            elif choice == '2':
                self.auto_video_generation()
            elif choice == '3':
                self.audio_only()
            elif choice == '4':
                self.image_only()
            elif choice == '5':
                self.project_manager()
            elif choice == '6':
                self.settings_menu()
            elif choice == '7':
                self.api_configuration()
            elif choice == '8':
                self.show_help()
            elif choice == '0':
                print_info("Goodbye!")
                sys.exit(0)

    # ═══════════════════════════════════════════════════════════════
    # FEATURE 1: SYNC VIDEO CREATOR (Main Feature)
    # ═══════════════════════════════════════════════════════════════

    def sync_video_creator(self):
        """Create perfectly synced video from audio + images"""
        print_header()
        print(f"""
{Colors.BOLD}╔═══════════════════════════════════════════════════════════════╗
║                   SYNC VIDEO CREATOR                          ║
║          Upload Audio + Images → Perfect Synced Video         ║
╠═══════════════════════════════════════════════════════════════╣
║  ✓ Word-by-word audio analysis                                ║
║  ✓ Perfect image-voice synchronization                        ║
║  ✓ No time limit (4-5 hours supported)                        ║
║  ✓ Supports MP3, WAV, M4A, FLAC audio                         ║
║  ✓ Supports JPG, PNG, WEBP images                             ║
╚═══════════════════════════════════════════════════════════════╝{Colors.END}
""")

        # Step 1: Get audio file
        print(f"{Colors.CYAN}STEP 1: Select Audio File{Colors.END}")
        print("Enter the path to your audio file (MP3, WAV, M4A, FLAC):")
        audio_path = input(f"{Colors.YELLOW}Audio path: {Colors.END}").strip().strip('"').strip("'")

        if not os.path.isfile(audio_path):
            print_error("Audio file not found!")
            input("\nPress Enter to continue...")
            return

        # Verify audio
        duration = AudioAnalyzer.get_audio_duration(audio_path)
        if duration <= 0:
            print_error("Invalid audio file!")
            input("\nPress Enter to continue...")
            return

        print_success(f"Audio loaded: {format_time(duration)} duration")

        # Step 2: Get images folder
        print(f"\n{Colors.CYAN}STEP 2: Select Images Folder{Colors.END}")
        print("Enter the path to folder containing your images:")
        print(f"{Colors.YELLOW}(Images will be used in alphabetical/numerical order){Colors.END}")
        images_folder = input(f"{Colors.YELLOW}Images folder: {Colors.END}").strip().strip('"').strip("'")

        if not os.path.isdir(images_folder):
            print_error("Folder not found!")
            input("\nPress Enter to continue...")
            return

        # Get images
        images = VideoGenerator.get_image_files(images_folder)

        if not images:
            print_error("No images found in folder!")
            print_info("Supported formats: JPG, PNG, WEBP, BMP, GIF")
            input("\nPress Enter to continue...")
            return

        print_success(f"Found {len(images)} images")

        # Preview images
        print(f"\n{Colors.CYAN}Image Order Preview:{Colors.END}")
        for i, img in enumerate(images[:10], 1):
            print(f"  {i}. {os.path.basename(img)}")
        if len(images) > 10:
            print(f"  ... and {len(images) - 10} more images")

        # Step 3: Sync settings
        print(f"\n{Colors.CYAN}STEP 3: Sync Settings{Colors.END}")
        print(f"""
How should images be synced with audio?

  {Colors.BOLD}[1] Smart Sync (Recommended){Colors.END}
      - Analyzes audio word-by-word
      - Each image shows during specific words
      - Requires OpenAI API key for best results

  {Colors.BOLD}[2] Even Distribution{Colors.END}
      - Divides audio evenly among images
      - Simple but less accurate
      - No API required
""")

        sync_choice = input(f"{Colors.YELLOW}Choose sync mode [1]: {Colors.END}").strip() or "1"

        # Get OpenAI key for smart sync
        openai_key = None
        if sync_choice == "1":
            openai_key = self.config["api_keys"].get("openai", "")
            if not openai_key:
                print(f"\n{Colors.YELLOW}OpenAI API key not configured.{Colors.END}")
                print("Enter OpenAI API key for smart sync (or press Enter for even distribution):")
                openai_key = input("OpenAI Key: ").strip()
                if openai_key:
                    self.config["api_keys"]["openai"] = openai_key
                    save_config(self.config)

        # Step 4: Output settings
        print(f"\n{Colors.CYAN}STEP 4: Output Settings{Colors.END}")

        resolution = self.config["settings"].get("video_resolution", "1920x1080")
        new_res = input(f"Resolution [{resolution}]: ").strip()
        if new_res:
            resolution = new_res

        # Create project
        project_name = f"sync_video_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        project_dir = PROJECTS_DIR / project_name
        project_dir.mkdir(parents=True, exist_ok=True)

        output_path = str(project_dir / "final_video.mp4")

        # Confirm
        print(f"""
{Colors.BOLD}╔═══════════════ SUMMARY ═══════════════╗{Colors.END}
  Audio: {os.path.basename(audio_path)}
  Duration: {format_time(duration)}
  Images: {len(images)} files
  Sync Mode: {"Smart Sync" if sync_choice == "1" and openai_key else "Even Distribution"}
  Resolution: {resolution}
  Output: {output_path}
{Colors.BOLD}╚═══════════════════════════════════════╝{Colors.END}
""")

        confirm = input(f"{Colors.YELLOW}Start video creation? (Y/n): {Colors.END}").strip().lower()
        if confirm == 'n':
            print_info("Cancelled.")
            input("\nPress Enter to continue...")
            return

        # Create video
        print(f"\n{Colors.CYAN}{'='*50}{Colors.END}")
        print(f"{Colors.BOLD}Creating Synced Video...{Colors.END}")
        print(f"{Colors.CYAN}{'='*50}{Colors.END}\n")

        success, info = VideoGenerator.create_long_video(
            images=images,
            audio_path=audio_path,
            output_path=output_path,
            resolution=resolution,
            openai_key=openai_key if sync_choice == "1" else None
        )

        if success:
            print(f"""
{Colors.GREEN}╔═══════════════════════════════════════════════════════════════╗
║                  VIDEO CREATED SUCCESSFULLY!                  ║
╠═══════════════════════════════════════════════════════════════╣
║  📁 Path: {output_path[:50]}...
║  ⏱️  Duration: {info['duration_formatted']}
║  📊 Size: {info['file_size_mb']:.1f} MB
║  🖼️  Images: {info['num_images']}
║  📐 Resolution: {info['resolution']}
╚═══════════════════════════════════════════════════════════════╝{Colors.END}
""")
        else:
            print_error("Video creation failed!")

        input("\nPress Enter to continue...")

    # ═══════════════════════════════════════════════════════════════
    # FEATURE 2: AUTO VIDEO GENERATION
    # ═══════════════════════════════════════════════════════════════

    def auto_video_generation(self):
        """Full auto video generation with AI"""
        print_header()
        print(f"""
{Colors.BOLD}╔═══════════ AUTO VIDEO GENERATOR ═══════════╗{Colors.END}
║  AI generates images + voice automatically    ║
╚═══════════════════════════════════════════════╝
""")

        if not self.elevenlabs or not self.ideogram:
            print_error("Please configure ElevenLabs and Ideogram APIs first!")
            print_info("Go to [7] API Configuration")
            input("\nPress Enter to continue...")
            return

        # Get script
        print(f"{Colors.CYAN}Enter your script (press Enter twice to finish):{Colors.END}\n")
        lines = []
        while True:
            line = input()
            if line == "":
                if lines:
                    break
            else:
                lines.append(line)

        script = "\n".join(lines)
        if not script.strip():
            print_error("No script provided!")
            input("\nPress Enter to continue...")
            return

        # Number of images
        num_images = input(f"\n{Colors.CYAN}Number of images [6]: {Colors.END}").strip()
        num_images = int(num_images) if num_images.isdigit() else 6

        # Create project
        project_name = f"auto_video_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        project_dir = PROJECTS_DIR / project_name
        project_dir.mkdir(parents=True, exist_ok=True)

        images_dir = project_dir / "images"
        images_dir.mkdir(exist_ok=True)

        audio_path = str(project_dir / "audio.mp3")
        video_path = str(project_dir / "final_video.mp4")

        # Generate audio
        print(f"\n{Colors.CYAN}Step 1: Generating voice...{Colors.END}")
        voice_id = self.config["api_keys"].get("elevenlabs_voice_id", "")

        if self.elevenlabs.generate_speech(script, voice_id, audio_path):
            print_success("Audio generated!")
        else:
            print_error("Audio generation failed!")
            input("\nPress Enter to continue...")
            return

        # Generate images
        print(f"\n{Colors.CYAN}Step 2: Generating {num_images} images...{Colors.END}")
        prompts = self._generate_prompts(script, num_images)

        images = []
        for i, prompt in enumerate(prompts):
            progress_bar(i, len(prompts), "Generating")
            output_path = images_dir / f"image_{i+1:03d}.png"
            if self.ideogram.generate_image(prompt, str(output_path)):
                images.append(str(output_path))
            time.sleep(1)

        progress_bar(len(prompts), len(prompts), "Generating")
        print_success(f"Generated {len(images)} images")

        # Create video
        print(f"\n{Colors.CYAN}Step 3: Creating video...{Colors.END}")

        success, info = VideoGenerator.create_long_video(
            images=images,
            audio_path=audio_path,
            output_path=video_path,
            resolution=self.config["settings"].get("video_resolution", "1920x1080"),
            openai_key=self.config["api_keys"].get("openai")
        )

        if success:
            print(f"""
{Colors.GREEN}╔═══════════════════════════════════════════════════╗
║            VIDEO CREATED SUCCESSFULLY!            ║
╠═══════════════════════════════════════════════════╣
║  📁 Path: {video_path}
║  ⏱️  Duration: {info['duration_formatted']}
║  📊 Size: {info['file_size_mb']:.1f} MB
╚═══════════════════════════════════════════════════╝{Colors.END}
""")
        else:
            print_error("Video creation failed!")

        input("\nPress Enter to continue...")

    def _generate_prompts(self, script: str, num: int) -> List[str]:
        """Generate image prompts from script"""
        words = script.split()
        chunk_size = max(1, len(words) // num)
        prompts = []
        style = "cinematic, high quality, 8K, detailed"

        for i in range(num):
            start = i * chunk_size
            chunk = ' '.join(words[start:start + chunk_size]).lower()

            if any(w in chunk for w in ['morning', 'sunrise', 'wake']):
                prompts.append(f"Beautiful morning scene, golden hour, {style}")
            elif any(w in chunk for w in ['night', 'dark', 'sleep']):
                prompts.append(f"Peaceful night scene, moonlight, {style}")
            elif any(w in chunk for w in ['city', 'urban', 'street']):
                prompts.append(f"Urban cityscape, modern, {style}")
            elif any(w in chunk for w in ['nature', 'forest', 'mountain']):
                prompts.append(f"Natural landscape, scenic, {style}")
            else:
                prompts.append(f"Atmospheric cinematic scene, {style}")

        return prompts

    # ═══════════════════════════════════════════════════════════════
    # FEATURE 3: AUDIO ONLY
    # ═══════════════════════════════════════════════════════════════

    def audio_only(self):
        """Generate audio only"""
        print_header()
        print(f"{Colors.BOLD}╔═══════════ AUDIO GENERATOR ═══════════╗{Colors.END}")

        if not self.elevenlabs:
            print_error("ElevenLabs API not configured!")
            input("\nPress Enter to continue...")
            return

        voice_id = self.config["api_keys"].get("elevenlabs_voice_id", "")
        if not voice_id:
            print_error("Voice ID not configured!")
            input("\nPress Enter to continue...")
            return

        print(f"\n{Colors.CYAN}Enter text (press Enter twice to finish):{Colors.END}\n")
        lines = []
        while True:
            line = input()
            if line == "":
                if lines:
                    break
            else:
                lines.append(line)

        text = "\n".join(lines)
        if not text.strip():
            print_error("No text provided!")
            input("\nPress Enter to continue...")
            return

        output_name = f"audio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"
        output_path = PROJECTS_DIR / output_name

        print(f"\n{Colors.CYAN}Generating audio...{Colors.END}")

        if self.elevenlabs.generate_speech(text, voice_id, str(output_path)):
            duration = AudioAnalyzer.get_audio_duration(str(output_path))
            size_kb = output_path.stat().st_size / 1024
            print_success(f"Audio saved: {output_path}")
            print_info(f"Duration: {format_time(duration)}, Size: {size_kb:.1f} KB")
        else:
            print_error("Audio generation failed!")

        input("\nPress Enter to continue...")

    # ═══════════════════════════════════════════════════════════════
    # FEATURE 4: IMAGE ONLY
    # ═══════════════════════════════════════════════════════════════

    def image_only(self):
        """Generate images only"""
        print_header()
        print(f"{Colors.BOLD}╔═══════════ IMAGE GENERATOR ═══════════╗{Colors.END}")

        if not self.ideogram:
            print_error("Ideogram API not configured!")
            input("\nPress Enter to continue...")
            return

        print(f"""
{Colors.BOLD}Select mode:{Colors.END}
  [1] Single image
  [2] Batch images
""")
        mode = input("Choice [1]: ").strip() or "1"

        output_dir = PROJECTS_DIR / f"images_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        output_dir.mkdir(parents=True, exist_ok=True)

        if mode == "1":
            prompt = input(f"\n{Colors.CYAN}Enter prompt: {Colors.END}").strip()
            if not prompt:
                return

            output_path = output_dir / "image.png"
            print(f"\n{Colors.CYAN}Generating...{Colors.END}")

            if self.ideogram.generate_image(prompt, str(output_path)):
                print_success(f"Image saved: {output_path}")
            else:
                print_error("Generation failed!")
        else:
            num = input(f"\n{Colors.CYAN}How many images? [5]: {Colors.END}").strip()
            num = int(num) if num.isdigit() else 5

            print(f"\n{Colors.CYAN}Enter {num} prompts:{Colors.END}")
            prompts = []
            for i in range(num):
                prompt = input(f"  {i+1}. ").strip()
                if prompt:
                    prompts.append(prompt)

            if not prompts:
                return

            print(f"\n{Colors.CYAN}Generating {len(prompts)} images...{Colors.END}")
            for i, prompt in enumerate(prompts):
                progress_bar(i, len(prompts), "Generating")
                output_path = output_dir / f"image_{i+1:03d}.png"
                self.ideogram.generate_image(prompt, str(output_path))
                time.sleep(1)

            progress_bar(len(prompts), len(prompts), "Generating")
            print_success(f"Images saved in: {output_dir}")

        input("\nPress Enter to continue...")

    # ═══════════════════════════════════════════════════════════════
    # PROJECT MANAGER
    # ═══════════════════════════════════════════════════════════════

    def project_manager(self):
        """Manage projects"""
        print_header()
        print(f"{Colors.BOLD}╔═══════════ PROJECT MANAGER ═══════════╗{Colors.END}\n")

        projects = sorted(PROJECTS_DIR.iterdir()) if PROJECTS_DIR.exists() else []
        projects = [p for p in projects if p.is_dir()]

        if not projects:
            print_info("No projects found.")
            input("\nPress Enter to continue...")
            return

        print(f"{Colors.BOLD}Your Projects:{Colors.END}\n")
        for i, project in enumerate(projects, 1):
            size = sum(f.stat().st_size for f in project.rglob('*') if f.is_file())
            size_mb = size / (1024 * 1024)
            print(f"  [{i}] {project.name} ({size_mb:.1f} MB)")

        print(f"""
{Colors.BOLD}Options:{Colors.END}
  [O] Open folder  [D] Delete  [B] Back
""")
        choice = input("Choice: ").strip().upper()

        if choice == 'O':
            idx = input("Project number: ").strip()
            if idx.isdigit() and 1 <= int(idx) <= len(projects):
                project = projects[int(idx) - 1]
                if os.name == 'nt':
                    os.startfile(project)
                else:
                    subprocess.run(['xdg-open', str(project)])

        elif choice == 'D':
            idx = input("Project number to delete: ").strip()
            if idx.isdigit() and 1 <= int(idx) <= len(projects):
                confirm = input(f"Delete '{projects[int(idx)-1].name}'? (y/N): ").strip().lower()
                if confirm == 'y':
                    shutil.rmtree(projects[int(idx) - 1])
                    print_success("Deleted!")

        input("\nPress Enter to continue...")

    # ═══════════════════════════════════════════════════════════════
    # SETTINGS
    # ═══════════════════════════════════════════════════════════════

    def settings_menu(self):
        """Settings menu"""
        while True:
            print_header()
            print(f"""
{Colors.BOLD}╔═══════════════ SETTINGS ═══════════════╗{Colors.END}

  {Colors.CYAN}[1]{Colors.END} Video Resolution: {self.config['settings']['video_resolution']}
  {Colors.CYAN}[2]{Colors.END} Image Provider: {self.config['settings']['image_provider']}

  {Colors.CYAN}[0]{Colors.END} Back
""")
            choice = input("Choice: ").strip()

            if choice == '1':
                print("\n  [1] 1920x1080  [2] 1280x720  [3] 3840x2160")
                c = input("  Choice: ").strip()
                res = {'1': '1920x1080', '2': '1280x720', '3': '3840x2160'}
                if c in res:
                    self.config['settings']['video_resolution'] = res[c]
                    save_config(self.config)
                    print_success("Saved!")
            elif choice == '2':
                print("\n  [1] Ideogram  [2] Gemini")
                c = input("  Choice: ").strip()
                if c == '1':
                    self.config['settings']['image_provider'] = 'ideogram'
                elif c == '2':
                    self.config['settings']['image_provider'] = 'gemini'
                save_config(self.config)
                print_success("Saved!")
            elif choice == '0':
                break

    # ═══════════════════════════════════════════════════════════════
    # API CONFIGURATION
    # ═══════════════════════════════════════════════════════════════

    def api_configuration(self):
        """Configure API keys"""
        print_header()
        print(f"{Colors.BOLD}╔═══════════ API CONFIGURATION ═══════════╗{Colors.END}\n")

        apis = [
            ("ElevenLabs API Key", "elevenlabs"),
            ("ElevenLabs Voice ID", "elevenlabs_voice_id"),
            ("Ideogram API Key", "ideogram"),
            ("Gemini API Key", "gemini"),
            ("OpenAI API Key (for Smart Sync)", "openai")
        ]

        for i, (name, key) in enumerate(apis, 1):
            current = self.config["api_keys"].get(key, "")
            display = current[:15] + "..." if current else "Not set"
            print(f"{Colors.CYAN}{i}. {name}{Colors.END} [{display}]")
            new_val = input("   New value (Enter to skip): ").strip()
            if new_val:
                self.config["api_keys"][key] = new_val

        save_config(self.config)
        self._init_apis()
        print_success("\nConfiguration saved!")
        input("\nPress Enter to continue...")

    # ═══════════════════════════════════════════════════════════════
    # HELP
    # ═══════════════════════════════════════════════════════════════

    def show_help(self):
        """Show help"""
        print_header()
        print(f"""
{Colors.BOLD}╔═══════════════════ HELP ═══════════════════╗{Colors.END}

{Colors.CYAN}MAIN FEATURE: Sync Video Creator{Colors.END}

  This tool creates perfectly synced videos from:
  - Your own audio file (MP3, WAV, M4A, FLAC)
  - Your own images (JPG, PNG, WEBP)

  {Colors.BOLD}How it works:{Colors.END}
  1. Upload your audio file
  2. Upload folder with images
  3. Tool analyzes audio word-by-word
  4. Each image syncs perfectly with voice
  5. Creates professional video

  {Colors.BOLD}Supported:{Colors.END}
  - Any duration (4-5 hours supported)
  - Unlimited images
  - Word-level sync accuracy

{Colors.CYAN}REQUIREMENTS:{Colors.END}

  - Python 3.8+
  - FFmpeg (for video creation)
  - OpenAI API Key (for smart sync) - optional

{Colors.CYAN}API KEYS:{Colors.END}

  - ElevenLabs: https://elevenlabs.io
  - Ideogram: https://ideogram.ai/api
  - OpenAI: https://platform.openai.com/api-keys

╚═════════════════════════════════════════════╝
""")
        input("\nPress Enter to continue...")


# ═══════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════

def main():
    try:
        app = AIVideoStudio()
        app.main_menu()
    except KeyboardInterrupt:
        print("\n\nGoodbye!")
        sys.exit(0)

if __name__ == "__main__":
    main()
