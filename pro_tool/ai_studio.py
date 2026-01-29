#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════╗
║                    AI VIDEO STUDIO PRO                           ║
║                  Professional Video Generator                     ║
╠══════════════════════════════════════════════════════════════════╣
║  Features:                                                        ║
║  1. Bulk Image + Voice → Video (Word-by-word sync)               ║
║  2. Auto Video Generation (API images + voice)                   ║
║  3. Audio Only Generation (ElevenLabs)                           ║
║  4. Image Only Generation (Ideogram/Gemini)                      ║
║  5. Text-to-Speech with multiple voices                          ║
║  6. Project Management                                            ║
║  7. Batch Processing                                              ║
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
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import threading

# ═══════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════

APP_NAME = "AI Video Studio Pro"
VERSION = "2.0.0"
CONFIG_FILE = Path(__file__).parent / "config.json"
PROJECTS_DIR = Path(__file__).parent / "projects"
TEMP_DIR = Path(__file__).parent / "temp"

# Default config
DEFAULT_CONFIG = {
    "api_keys": {
        "elevenlabs": "",
        "elevenlabs_voice_id": "",
        "ideogram": "",
        "gemini": ""
    },
    "settings": {
        "image_provider": "ideogram",
        "default_voice_model": "eleven_monolingual_v1",
        "video_resolution": "1920x1080",
        "video_fps": 30,
        "image_duration": 5,
        "output_format": "mp4",
        "auto_enhance": True
    },
    "voices": {}
}

# ═══════════════════════════════════════════════════════════════════
# UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════

class Colors:
    """Terminal colors"""
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
    percent = current / total
    filled = int(length * percent)
    bar = '█' * filled + '░' * (length - filled)
    print(f'\r{prefix} |{bar}| {percent*100:.1f}%', end='', flush=True)
    if current == total:
        print()

def load_config():
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
            # Merge with defaults
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
# API CLASSES
# ═══════════════════════════════════════════════════════════════════

class ElevenLabsAPI:
    """ElevenLabs Text-to-Speech API"""

    BASE_URL = "https://api.elevenlabs.io/v1"

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "xi-api-key": api_key,
            "Content-Type": "application/json"
        }

    def get_voices(self) -> List[Dict]:
        """Get available voices"""
        try:
            response = requests.get(
                f"{self.BASE_URL}/voices",
                headers=self.headers,
                timeout=30
            )
            if response.status_code == 200:
                return response.json().get("voices", [])
        except Exception as e:
            print_error(f"Failed to get voices: {e}")
        return []

    def generate_speech(self, text: str, voice_id: str, output_path: str,
                       model: str = "eleven_monolingual_v1") -> bool:
        """Generate speech from text"""
        url = f"{self.BASE_URL}/text-to-speech/{voice_id}"

        data = {
            "text": text,
            "model_id": model,
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75,
                "style": 0.0,
                "use_speaker_boost": True
            }
        }

        headers = {
            "Accept": "audio/mpeg",
            "xi-api-key": self.api_key,
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(url, json=data, headers=headers, timeout=120)

            if response.status_code == 200:
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                return True
            else:
                print_error(f"ElevenLabs Error: {response.status_code}")
                return False
        except Exception as e:
            print_error(f"Error: {e}")
            return False

    def generate_speech_with_timestamps(self, text: str, voice_id: str,
                                        output_path: str) -> Optional[Dict]:
        """Generate speech with word timestamps"""
        url = f"{self.BASE_URL}/text-to-speech/{voice_id}/with-timestamps"

        data = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75
            }
        }

        headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(url, json=data, headers=headers, timeout=120)

            if response.status_code == 200:
                result = response.json()
                # Save audio
                audio_base64 = result.get("audio_base64", "")
                if audio_base64:
                    with open(output_path, 'wb') as f:
                        f.write(base64.b64decode(audio_base64))
                return result
            else:
                print_error(f"Error: {response.status_code}")
                return None
        except Exception as e:
            print_error(f"Error: {e}")
            return None


class IdeogramAPI:
    """Ideogram Image Generation API"""

    BASE_URL = "https://api.ideogram.ai"

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "Api-Key": api_key,
            "Content-Type": "application/json"
        }

    def generate_image(self, prompt: str, output_path: str,
                      aspect_ratio: str = "ASPECT_16_9",
                      style: str = "REALISTIC") -> bool:
        """Generate single image"""
        url = f"{self.BASE_URL}/generate"

        data = {
            "image_request": {
                "prompt": prompt,
                "aspect_ratio": aspect_ratio,
                "model": "V_2",
                "magic_prompt_option": "AUTO",
                "style_type": style
            }
        }

        for attempt in range(3):
            try:
                response = requests.post(url, json=data, headers=self.headers, timeout=120)

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
            except Exception as e:
                time.sleep(2)

        return False

    def generate_batch(self, prompts: List[str], output_dir: Path,
                      callback=None) -> List[str]:
        """Generate multiple images"""
        generated = []

        for i, prompt in enumerate(prompts):
            output_path = output_dir / f"image_{i+1:03d}.png"

            if callback:
                callback(i + 1, len(prompts))

            if self.generate_image(prompt, str(output_path)):
                generated.append(str(output_path))

            time.sleep(1)

        return generated


class GeminiAPI:
    """Google Gemini Image Generation API"""

    def __init__(self, api_key: str):
        self.api_key = api_key

    def generate_image(self, prompt: str, output_path: str) -> bool:
        """Generate image using Gemini"""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/imagen-3.0-generate-001:generateImages?key={self.api_key}"

        data = {
            "prompt": prompt,
            "number_of_images": 1,
            "aspect_ratio": "16:9"
        }

        try:
            response = requests.post(url, json=data,
                                   headers={"Content-Type": "application/json"},
                                   timeout=60)

            if response.status_code == 200:
                result = response.json()
                if 'generatedImages' in result and len(result['generatedImages']) > 0:
                    image_data = result['generatedImages'][0].get('image', {}).get('imageBytes', '')
                    if image_data:
                        with open(output_path, 'wb') as f:
                            f.write(base64.b64decode(image_data))
                        return True
        except Exception as e:
            pass

        return False


# ═══════════════════════════════════════════════════════════════════
# VIDEO GENERATOR
# ═══════════════════════════════════════════════════════════════════

class VideoGenerator:
    """Video generation utilities"""

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
    def create_video_from_images(images: List[str], audio_path: str,
                                 output_path: str, fps: int = 30) -> bool:
        """Create video from images with audio"""
        if not images:
            return False

        duration = VideoGenerator.get_audio_duration(audio_path)
        image_duration = duration / len(images)

        # Create concat file
        concat_file = Path(output_path).parent / "concat.txt"
        with open(concat_file, 'w') as f:
            for img in images:
                f.write(f"file '{img}'\n")
                f.write(f"duration {image_duration}\n")
            f.write(f"file '{images[-1]}'\n")

        cmd = [
            'ffmpeg', '-y',
            '-f', 'concat', '-safe', '0',
            '-i', str(concat_file),
            '-i', audio_path,
            '-vf', 'scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2',
            '-c:v', 'libx264', '-preset', 'medium',
            '-pix_fmt', 'yuv420p',
            '-c:a', 'aac', '-b:a', '192k',
            '-shortest',
            '-movflags', '+faststart',
            output_path
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        concat_file.unlink(missing_ok=True)

        return result.returncode == 0

    @staticmethod
    def create_synced_video(images: List[str], audio_path: str,
                           timestamps: List[Dict], output_path: str) -> bool:
        """Create video with word-synced images"""
        if not images or not timestamps:
            return False

        # Create concat file with precise timing
        concat_file = Path(output_path).parent / "concat.txt"

        # Calculate timing for each image
        num_images = len(images)
        num_words = len(timestamps)
        words_per_image = max(1, num_words // num_images)

        with open(concat_file, 'w') as f:
            for i, img in enumerate(images):
                start_word = i * words_per_image
                end_word = min((i + 1) * words_per_image, num_words)

                if start_word < num_words:
                    start_time = timestamps[start_word].get('start_time', i * 2)
                    if end_word < num_words:
                        end_time = timestamps[end_word].get('start_time', (i + 1) * 2)
                    else:
                        end_time = timestamps[-1].get('end_time', (i + 1) * 2)

                    duration = end_time - start_time
                else:
                    duration = 2

                f.write(f"file '{img}'\n")
                f.write(f"duration {duration}\n")

            f.write(f"file '{images[-1]}'\n")

        cmd = [
            'ffmpeg', '-y',
            '-f', 'concat', '-safe', '0',
            '-i', str(concat_file),
            '-i', audio_path,
            '-vf', 'scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2',
            '-c:v', 'libx264', '-preset', 'medium',
            '-pix_fmt', 'yuv420p',
            '-c:a', 'aac', '-b:a', '192k',
            '-shortest',
            '-movflags', '+faststart',
            output_path
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        concat_file.unlink(missing_ok=True)

        return result.returncode == 0


# ═══════════════════════════════════════════════════════════════════
# MAIN APPLICATION
# ═══════════════════════════════════════════════════════════════════

class AIVideoStudio:
    """Main Application Class"""

    def __init__(self):
        ensure_dirs()
        self.config = load_config()
        self.elevenlabs = None
        self.ideogram = None
        self.gemini = None
        self._init_apis()

    def _init_apis(self):
        """Initialize API clients"""
        if self.config["api_keys"].get("elevenlabs"):
            self.elevenlabs = ElevenLabsAPI(self.config["api_keys"]["elevenlabs"])

        if self.config["api_keys"].get("ideogram"):
            self.ideogram = IdeogramAPI(self.config["api_keys"]["ideogram"])

        if self.config["api_keys"].get("gemini"):
            self.gemini = GeminiAPI(self.config["api_keys"]["gemini"])

    def main_menu(self):
        """Display main menu"""
        while True:
            print_header()
            print(f"""
{Colors.BOLD}╔════════════════════ MAIN MENU ════════════════════╗{Colors.END}
║                                                     ║
║  {Colors.CYAN}[1]{Colors.END} 🎬 Create Video (Bulk Images + Voice)         ║
║  {Colors.CYAN}[2]{Colors.END} 🤖 Auto Video (AI Images + AI Voice)          ║
║  {Colors.CYAN}[3]{Colors.END} 🎙️  Generate Audio Only                        ║
║  {Colors.CYAN}[4]{Colors.END} 🖼️  Generate Images Only                       ║
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
                self.bulk_image_video()
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
    # FEATURE 1: BULK IMAGE + VOICE VIDEO
    # ═══════════════════════════════════════════════════════════════

    def bulk_image_video(self):
        """Create video from bulk images + voice"""
        print_header()
        print(f"""
{Colors.BOLD}╔═══════════ BULK IMAGE VIDEO CREATOR ═══════════╗{Colors.END}
║  Create video from your images + AI voice        ║
╚══════════════════════════════════════════════════╝
""")

        # Get image folder
        print_info("Enter folder path containing images:")
        image_folder = input("Path: ").strip()

        if not os.path.isdir(image_folder):
            print_error("Invalid folder path!")
            input("\nPress Enter to continue...")
            return

        # Get images
        valid_extensions = {'.jpg', '.jpeg', '.png', '.webp', '.bmp'}
        images = sorted([
            os.path.join(image_folder, f) for f in os.listdir(image_folder)
            if os.path.splitext(f)[1].lower() in valid_extensions
        ])

        if not images:
            print_error("No images found in folder!")
            input("\nPress Enter to continue...")
            return

        print_success(f"Found {len(images)} images")

        # Get script
        print(f"\n{Colors.CYAN}Enter your script (press Enter twice to finish):{Colors.END}\n")
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

        # Sync mode
        print(f"""
{Colors.BOLD}Select sync mode:{Colors.END}
  [1] Even distribution (each image shows for equal time)
  [2] Word-by-word sync (match words to images)
""")
        sync_mode = input("Choice [1]: ").strip() or "1"

        # Create project folder
        project_name = f"bulk_video_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        project_dir = PROJECTS_DIR / project_name
        project_dir.mkdir(parents=True, exist_ok=True)

        audio_path = project_dir / "audio.mp3"
        video_path = project_dir / "final_video.mp4"

        # Generate audio
        print(f"\n{Colors.CYAN}Generating voice...{Colors.END}")

        if not self.elevenlabs:
            print_error("ElevenLabs API not configured!")
            input("\nPress Enter to continue...")
            return

        voice_id = self.config["api_keys"].get("elevenlabs_voice_id", "")
        if not voice_id:
            print_error("Voice ID not configured!")
            input("\nPress Enter to continue...")
            return

        if sync_mode == "2":
            # Word-by-word sync
            result = self.elevenlabs.generate_speech_with_timestamps(
                script, voice_id, str(audio_path)
            )
            if result:
                timestamps = result.get("alignment", {}).get("characters", [])
                print_success("Audio generated with timestamps!")

                print(f"\n{Colors.CYAN}Creating synced video...{Colors.END}")
                if VideoGenerator.create_synced_video(images, str(audio_path),
                                                     timestamps, str(video_path)):
                    print_success(f"Video created: {video_path}")
                else:
                    print_error("Video creation failed!")
            else:
                print_error("Failed to generate audio!")
        else:
            # Even distribution
            if self.elevenlabs.generate_speech(script, voice_id, str(audio_path)):
                print_success("Audio generated!")

                print(f"\n{Colors.CYAN}Creating video...{Colors.END}")
                if VideoGenerator.create_video_from_images(images, str(audio_path),
                                                          str(video_path)):
                    print_success(f"Video created: {video_path}")
                else:
                    print_error("Video creation failed!")
            else:
                print_error("Failed to generate audio!")

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
        num_images = input(f"\n{Colors.CYAN}Number of images to generate [6]: {Colors.END}").strip()
        num_images = int(num_images) if num_images.isdigit() else 6

        # Get image prompts
        print(f"""
{Colors.BOLD}Image prompt mode:{Colors.END}
  [1] Auto-generate prompts from script
  [2] Enter custom prompts
""")
        prompt_mode = input("Choice [1]: ").strip() or "1"

        prompts = []
        if prompt_mode == "2":
            print(f"\n{Colors.CYAN}Enter {num_images} image prompts:{Colors.END}")
            for i in range(num_images):
                prompt = input(f"  {i+1}. ").strip()
                if prompt:
                    prompts.append(prompt)

        if len(prompts) < num_images:
            # Auto-generate remaining
            prompts = self._generate_prompts_from_script(script, num_images)

        # Create project
        project_name = f"auto_video_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        project_dir = PROJECTS_DIR / project_name
        project_dir.mkdir(parents=True, exist_ok=True)

        images_dir = project_dir / "images"
        images_dir.mkdir(exist_ok=True)

        audio_path = project_dir / "audio.mp3"
        video_path = project_dir / "final_video.mp4"

        # Generate audio
        print(f"\n{Colors.CYAN}Step 1: Generating voice...{Colors.END}")

        if not self.elevenlabs:
            print_error("ElevenLabs API not configured!")
            input("\nPress Enter to continue...")
            return

        voice_id = self.config["api_keys"].get("elevenlabs_voice_id", "")
        if self.elevenlabs.generate_speech(script, voice_id, str(audio_path)):
            print_success("Audio generated!")
        else:
            print_error("Failed to generate audio!")
            input("\nPress Enter to continue...")
            return

        # Generate images
        print(f"\n{Colors.CYAN}Step 2: Generating {num_images} images...{Colors.END}")

        image_api = self.ideogram if self.config["settings"]["image_provider"] == "ideogram" else self.gemini

        if not image_api:
            print_error("Image API not configured!")
            input("\nPress Enter to continue...")
            return

        images = []
        for i, prompt in enumerate(prompts):
            progress_bar(i, len(prompts), "Generating")
            output_path = images_dir / f"image_{i+1:03d}.png"

            if isinstance(image_api, IdeogramAPI):
                if image_api.generate_image(prompt, str(output_path)):
                    images.append(str(output_path))
            else:
                if image_api.generate_image(prompt, str(output_path)):
                    images.append(str(output_path))

            time.sleep(1)

        progress_bar(len(prompts), len(prompts), "Generating")
        print_success(f"Generated {len(images)} images")

        # Create video
        print(f"\n{Colors.CYAN}Step 3: Creating video...{Colors.END}")

        if VideoGenerator.create_video_from_images(images, str(audio_path), str(video_path)):
            duration = VideoGenerator.get_audio_duration(str(audio_path))
            size_mb = video_path.stat().st_size / (1024 * 1024)

            print(f"""
{Colors.GREEN}╔═══════════════════════════════════════════════════╗
║            VIDEO CREATED SUCCESSFULLY!            ║
╠═══════════════════════════════════════════════════╣
║  📁 Path: {str(video_path)[:40]}...
║  📊 Size: {size_mb:.2f} MB
║  ⏱️  Duration: {duration:.1f} seconds
║  🖼️  Images: {len(images)}
╚═══════════════════════════════════════════════════╝{Colors.END}
""")
        else:
            print_error("Video creation failed!")

        input("\nPress Enter to continue...")

    def _generate_prompts_from_script(self, script: str, num_prompts: int) -> List[str]:
        """Generate image prompts from script"""
        words = script.split()
        chunk_size = max(1, len(words) // num_prompts)

        prompts = []
        style = "cinematic, high quality, 8K, detailed, professional"

        keywords_map = {
            ('morning', 'wake', 'sunrise', 'dawn'): "Beautiful morning scene, golden hour lighting",
            ('night', 'dark', 'sleep', 'dream'): "Peaceful night scene, moonlight, serene",
            ('city', 'urban', 'street', 'building'): "Urban cityscape, modern architecture",
            ('nature', 'forest', 'tree', 'mountain'): "Stunning natural landscape, scenic view",
            ('home', 'house', 'room', 'interior'): "Cozy interior space, warm lighting",
            ('vintage', 'old', 'classic', 'retro'): "Vintage aesthetic, nostalgic atmosphere",
            ('future', 'modern', 'tech', 'digital'): "Futuristic scene, high-tech environment",
        }

        for i in range(num_prompts):
            start = i * chunk_size
            end = min(start + chunk_size, len(words))
            chunk = ' '.join(words[start:end]).lower()

            prompt = None
            for keywords, base_prompt in keywords_map.items():
                if any(kw in chunk for kw in keywords):
                    prompt = f"{base_prompt}, {style}"
                    break

            if not prompt:
                prompt = f"Atmospheric cinematic scene, storytelling mood, {style}"

            prompts.append(prompt)

        return prompts

    # ═══════════════════════════════════════════════════════════════
    # FEATURE 3: AUDIO ONLY
    # ═══════════════════════════════════════════════════════════════

    def audio_only(self):
        """Generate audio only"""
        print_header()
        print(f"""
{Colors.BOLD}╔═══════════ AUDIO GENERATOR ═══════════╗{Colors.END}
║  Generate voice using ElevenLabs AI    ║
╚════════════════════════════════════════╝
""")

        if not self.elevenlabs:
            print_error("ElevenLabs API not configured!")
            input("\nPress Enter to continue...")
            return

        # Show available voices
        print(f"{Colors.CYAN}Fetching available voices...{Colors.END}")
        voices = self.elevenlabs.get_voices()

        if voices:
            print(f"\n{Colors.BOLD}Available Voices:{Colors.END}")
            for i, voice in enumerate(voices[:10], 1):
                print(f"  [{i}] {voice['name']} - {voice['voice_id'][:20]}...")
            print()

        # Get voice ID
        voice_id = self.config["api_keys"].get("elevenlabs_voice_id", "")
        new_voice = input(f"Voice ID [{voice_id[:20] if voice_id else 'not set'}...]: ").strip()
        if new_voice:
            voice_id = new_voice

        if not voice_id:
            print_error("No voice ID provided!")
            input("\nPress Enter to continue...")
            return

        # Get text
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

        # Output path
        default_name = f"audio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"
        output_name = input(f"\nOutput filename [{default_name}]: ").strip() or default_name

        output_path = PROJECTS_DIR / output_name

        print(f"\n{Colors.CYAN}Generating audio...{Colors.END}")

        if self.elevenlabs.generate_speech(text, voice_id, str(output_path)):
            duration = VideoGenerator.get_audio_duration(str(output_path))
            size_kb = output_path.stat().st_size / 1024

            print(f"""
{Colors.GREEN}╔═══════════════════════════════════════════════════╗
║            AUDIO CREATED SUCCESSFULLY!            ║
╠═══════════════════════════════════════════════════╣
║  📁 Path: {str(output_path)}
║  📊 Size: {size_kb:.1f} KB
║  ⏱️  Duration: {duration:.1f} seconds
╚═══════════════════════════════════════════════════╝{Colors.END}
""")
        else:
            print_error("Audio generation failed!")

        input("\nPress Enter to continue...")

    # ═══════════════════════════════════════════════════════════════
    # FEATURE 4: IMAGE ONLY
    # ═══════════════════════════════════════════════════════════════

    def image_only(self):
        """Generate images only"""
        print_header()
        print(f"""
{Colors.BOLD}╔═══════════ IMAGE GENERATOR ═══════════╗{Colors.END}
║  Generate images using AI              ║
╚════════════════════════════════════════╝

{Colors.BOLD}Select mode:{Colors.END}
  [1] Single image
  [2] Batch images (multiple prompts)
""")

        mode = input("Choice [1]: ").strip() or "1"

        provider = self.config["settings"]["image_provider"]
        image_api = self.ideogram if provider == "ideogram" else self.gemini

        if not image_api:
            print_error(f"{provider.title()} API not configured!")
            input("\nPress Enter to continue...")
            return

        output_dir = PROJECTS_DIR / f"images_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        output_dir.mkdir(parents=True, exist_ok=True)

        if mode == "1":
            # Single image
            print(f"\n{Colors.CYAN}Enter image prompt:{Colors.END}")
            prompt = input("> ").strip()

            if not prompt:
                print_error("No prompt provided!")
                input("\nPress Enter to continue...")
                return

            output_path = output_dir / "image.png"

            print(f"\n{Colors.CYAN}Generating image...{Colors.END}")

            if isinstance(image_api, IdeogramAPI):
                success = image_api.generate_image(prompt, str(output_path))
            else:
                success = image_api.generate_image(prompt, str(output_path))

            if success:
                print_success(f"Image saved: {output_path}")
            else:
                print_error("Image generation failed!")

        else:
            # Batch images
            num = input(f"\n{Colors.CYAN}How many images? [5]: {Colors.END}").strip()
            num = int(num) if num.isdigit() else 5

            print(f"\n{Colors.CYAN}Enter {num} prompts:{Colors.END}")
            prompts = []
            for i in range(num):
                prompt = input(f"  {i+1}. ").strip()
                if prompt:
                    prompts.append(prompt)

            if not prompts:
                print_error("No prompts provided!")
                input("\nPress Enter to continue...")
                return

            print(f"\n{Colors.CYAN}Generating {len(prompts)} images...{Colors.END}")

            generated = []
            for i, prompt in enumerate(prompts):
                progress_bar(i, len(prompts), "Generating")
                output_path = output_dir / f"image_{i+1:03d}.png"

                if isinstance(image_api, IdeogramAPI):
                    if image_api.generate_image(prompt, str(output_path)):
                        generated.append(str(output_path))
                else:
                    if image_api.generate_image(prompt, str(output_path)):
                        generated.append(str(output_path))

                time.sleep(1)

            progress_bar(len(prompts), len(prompts), "Generating")
            print_success(f"Generated {len(generated)} images in: {output_dir}")

        input("\nPress Enter to continue...")

    # ═══════════════════════════════════════════════════════════════
    # PROJECT MANAGER
    # ═══════════════════════════════════════════════════════════════

    def project_manager(self):
        """Manage projects"""
        print_header()
        print(f"""
{Colors.BOLD}╔═══════════ PROJECT MANAGER ═══════════╗{Colors.END}
""")

        projects = sorted(PROJECTS_DIR.iterdir()) if PROJECTS_DIR.exists() else []

        if not projects:
            print_info("No projects found.")
            input("\nPress Enter to continue...")
            return

        print(f"{Colors.BOLD}Your Projects:{Colors.END}\n")

        for i, project in enumerate(projects, 1):
            if project.is_dir():
                size = sum(f.stat().st_size for f in project.rglob('*') if f.is_file())
                size_mb = size / (1024 * 1024)
                print(f"  [{i}] {project.name} ({size_mb:.1f} MB)")

        print(f"""
{Colors.BOLD}Options:{Colors.END}
  [O] Open project folder
  [D] Delete project
  [B] Back
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
                project = projects[int(idx) - 1]
                confirm = input(f"Delete '{project.name}'? (y/N): ").strip().lower()
                if confirm == 'y':
                    shutil.rmtree(project)
                    print_success("Project deleted!")

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

  {Colors.CYAN}[1]{Colors.END} Image Provider: {self.config['settings']['image_provider']}
  {Colors.CYAN}[2]{Colors.END} Video Resolution: {self.config['settings']['video_resolution']}
  {Colors.CYAN}[3]{Colors.END} Images per video: {self.config['settings'].get('images_count', 6)}
  {Colors.CYAN}[4]{Colors.END} Output Format: {self.config['settings']['output_format']}

  {Colors.CYAN}[0]{Colors.END} Back

╚═════════════════════════════════════════╝
""")

            choice = input("Choice: ").strip()

            if choice == '1':
                print("\n  [1] Ideogram\n  [2] Gemini")
                c = input("  Choice: ").strip()
                if c == '1':
                    self.config['settings']['image_provider'] = 'ideogram'
                elif c == '2':
                    self.config['settings']['image_provider'] = 'gemini'
                save_config(self.config)
                print_success("Setting saved!")

            elif choice == '2':
                print("\n  [1] 1920x1080\n  [2] 1280x720\n  [3] 3840x2160")
                c = input("  Choice: ").strip()
                resolutions = {'1': '1920x1080', '2': '1280x720', '3': '3840x2160'}
                if c in resolutions:
                    self.config['settings']['video_resolution'] = resolutions[c]
                    save_config(self.config)
                    print_success("Setting saved!")

            elif choice == '3':
                num = input("  Number of images [6]: ").strip()
                if num.isdigit():
                    self.config['settings']['images_count'] = int(num)
                    save_config(self.config)
                    print_success("Setting saved!")

            elif choice == '0':
                break

    # ═══════════════════════════════════════════════════════════════
    # API CONFIGURATION
    # ═══════════════════════════════════════════════════════════════

    def api_configuration(self):
        """Configure API keys"""
        print_header()
        print(f"""
{Colors.BOLD}╔═══════════ API CONFIGURATION ═══════════╗{Colors.END}

Configure your API keys below.
Press Enter to keep existing value.

""")

        # ElevenLabs
        current = self.config["api_keys"].get("elevenlabs", "")
        display = current[:15] + "..." if current else "Not set"
        print(f"{Colors.CYAN}1. ElevenLabs API Key{Colors.END} [{display}]")
        key = input("   New value: ").strip()
        if key:
            self.config["api_keys"]["elevenlabs"] = key

        # Voice ID
        current = self.config["api_keys"].get("elevenlabs_voice_id", "")
        display = current if current else "Not set"
        print(f"\n{Colors.CYAN}2. ElevenLabs Voice ID{Colors.END} [{display}]")
        key = input("   New value: ").strip()
        if key:
            self.config["api_keys"]["elevenlabs_voice_id"] = key

        # Ideogram
        current = self.config["api_keys"].get("ideogram", "")
        display = current[:15] + "..." if current else "Not set"
        print(f"\n{Colors.CYAN}3. Ideogram API Key{Colors.END} [{display}]")
        key = input("   New value: ").strip()
        if key:
            self.config["api_keys"]["ideogram"] = key

        # Gemini
        current = self.config["api_keys"].get("gemini", "")
        display = current[:15] + "..." if current else "Not set"
        print(f"\n{Colors.CYAN}4. Gemini API Key{Colors.END} [{display}]")
        key = input("   New value: ").strip()
        if key:
            self.config["api_keys"]["gemini"] = key

        save_config(self.config)
        self._init_apis()

        print_success("\nAPI configuration saved!")
        input("\nPress Enter to continue...")

    # ═══════════════════════════════════════════════════════════════
    # HELP
    # ═══════════════════════════════════════════════════════════════

    def show_help(self):
        """Show help"""
        print_header()
        print(f"""
{Colors.BOLD}╔═══════════════════ HELP ═══════════════════╗{Colors.END}

{Colors.CYAN}FEATURES:{Colors.END}

{Colors.BOLD}1. Bulk Image Video{Colors.END}
   Upload your own images and add AI voice.
   Images will sync with voice automatically.

{Colors.BOLD}2. Auto Video Generation{Colors.END}
   Just provide a script - AI generates:
   - Images from your text
   - Voice narration
   - Complete video

{Colors.BOLD}3. Audio Only{Colors.END}
   Generate high-quality AI voice from text.
   Uses ElevenLabs API.

{Colors.BOLD}4. Image Only{Colors.END}
   Generate single or batch images.
   Uses Ideogram or Gemini API.

{Colors.CYAN}REQUIREMENTS:{Colors.END}

- Python 3.8+
- FFmpeg installed
- API Keys:
  * ElevenLabs (for voice)
  * Ideogram or Gemini (for images)

{Colors.CYAN}GETTING API KEYS:{Colors.END}

- ElevenLabs: https://elevenlabs.io
- Ideogram: https://ideogram.ai/api
- Gemini: https://makersuite.google.com/app/apikey

╚═════════════════════════════════════════════╝
""")
        input("\nPress Enter to continue...")


# ═══════════════════════════════════════════════════════════════════
# MAIN ENTRY POINT
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
