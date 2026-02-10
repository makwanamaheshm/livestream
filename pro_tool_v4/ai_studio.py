#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════╗
║              AI VIDEO STUDIO PRO v4.0 - INTELLIGENT SYNC             ║
║                    Smart Voice + Image Matching                       ║
╠══════════════════════════════════════════════════════════════════════╣
║  FEATURES:                                                            ║
║  ✓ Audio Analysis - Word-by-word transcription                       ║
║  ✓ Image Analysis - AI understands what's in each image              ║
║  ✓ Smart Matching - Auto-matches images with spoken words            ║
║  ✓ Auto Skip - Unused images are automatically skipped               ║
║  ✓ Perfect Sync - Right image at right time                          ║
╚══════════════════════════════════════════════════════════════════════╝
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
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

# ═══════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════

APP_NAME = "AI Video Studio Pro - Intelligent Sync"
VERSION = "4.0.0"
CONFIG_FILE = Path(__file__).parent / "config.json"
PROJECTS_DIR = Path(__file__).parent / "projects"
TEMP_DIR = Path(__file__).parent / "temp"

DEFAULT_CONFIG = {
    "api_keys": {
        "openai": "",
        "elevenlabs": "",
        "elevenlabs_voice_id": "",
        "ideogram": "",
        "gemini": ""
    },
    "settings": {
        "video_resolution": "1920x1080",
        "min_image_duration": 2.0,
        "max_image_duration": 15.0
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
    MAGENTA = '\033[35m'

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    clear_screen()
    print(f"""{Colors.CYAN}
╔══════════════════════════════════════════════════════════════════════╗
║              {Colors.BOLD}AI VIDEO STUDIO PRO v4.0{Colors.END}{Colors.CYAN}                            ║
║                 {Colors.YELLOW}INTELLIGENT VOICE-IMAGE SYNC{Colors.END}{Colors.CYAN}                       ║
╚══════════════════════════════════════════════════════════════════════╝{Colors.END}
""")

def print_success(msg):
    print(f"{Colors.GREEN}✓ {msg}{Colors.END}")

def print_error(msg):
    print(f"{Colors.RED}✗ {msg}{Colors.END}")

def print_info(msg):
    print(f"{Colors.BLUE}ℹ {msg}{Colors.END}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠ {msg}{Colors.END}")

def print_step(step, msg):
    print(f"\n{Colors.MAGENTA}[STEP {step}]{Colors.END} {Colors.BOLD}{msg}{Colors.END}")

def progress_bar(current, total, prefix='Progress', length=40):
    percent = current / total if total > 0 else 0
    filled = int(length * percent)
    bar = '█' * filled + '░' * (length - filled)
    print(f'\r{prefix} |{bar}| {percent*100:.1f}% ({current}/{total})', end='', flush=True)
    if current == total:
        print()

def format_time(seconds):
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
# DATA CLASSES
# ═══════════════════════════════════════════════════════════════════

@dataclass
class WordSegment:
    """Represents a word with its timestamp"""
    word: str
    start: float
    end: float

@dataclass
class TranscriptSegment:
    """Represents a segment of transcript (sentence/phrase)"""
    text: str
    start: float
    end: float
    words: List[WordSegment]

@dataclass
class ImageInfo:
    """Represents an analyzed image"""
    path: str
    filename: str
    description: str
    keywords: List[str]
    used: bool = False

@dataclass
class VideoSegment:
    """Represents a segment of the final video"""
    image_path: str
    start: float
    end: float
    transcript_text: str
    match_score: float

# ═══════════════════════════════════════════════════════════════════
# OPENAI API CLIENT
# ═══════════════════════════════════════════════════════════════════

class OpenAIClient:
    """OpenAI API client for transcription and vision"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def transcribe_audio(self, audio_path: str) -> Optional[Dict]:
        """
        Transcribe audio with word-level timestamps using Whisper API
        """
        print_info("Transcribing audio with OpenAI Whisper...")

        url = "https://api.openai.com/v1/audio/transcriptions"

        try:
            with open(audio_path, 'rb') as audio_file:
                response = requests.post(
                    url,
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    files={"file": audio_file},
                    data={
                        "model": "whisper-1",
                        "response_format": "verbose_json",
                        "timestamp_granularities[]": "word"
                    },
                    timeout=600
                )

            if response.status_code == 200:
                return response.json()
            else:
                print_error(f"Whisper API Error: {response.status_code}")
                print(response.text[:500])
                return None

        except Exception as e:
            print_error(f"Transcription error: {e}")
            return None

    def analyze_image(self, image_path: str) -> Optional[Dict]:
        """
        Analyze image using GPT-4 Vision to understand its content
        """
        url = "https://api.openai.com/v1/chat/completions"

        # Read and encode image
        with open(image_path, "rb") as img_file:
            image_data = base64.b64encode(img_file.read()).decode('utf-8')

        # Determine image type
        ext = os.path.splitext(image_path)[1].lower()
        media_type = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.webp': 'image/webp'
        }.get(ext, 'image/jpeg')

        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {
                    "role": "system",
                    "content": """You are an image analyzer. Analyze the image and provide:
1. A brief description (1-2 sentences)
2. Keywords that describe the image content (nouns, actions, themes)

Respond in JSON format:
{
    "description": "Brief description of what's in the image",
    "keywords": ["keyword1", "keyword2", "keyword3", ...]
}

Focus on: objects, people, actions, settings, themes, emotions, colors, time of day."""
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{media_type};base64,{image_data}",
                                "detail": "low"
                            }
                        },
                        {
                            "type": "text",
                            "text": "Analyze this image. Return JSON with description and keywords."
                        }
                    ]
                }
            ],
            "max_tokens": 300
        }

        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=60)

            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']

                # Parse JSON from response
                try:
                    # Try to extract JSON from response
                    json_match = re.search(r'\{.*\}', content, re.DOTALL)
                    if json_match:
                        return json.loads(json_match.group())
                except:
                    pass

                # Fallback: create basic structure
                return {
                    "description": content[:200],
                    "keywords": content.lower().split()[:10]
                }
            else:
                return None

        except Exception as e:
            return None

    def match_images_to_transcript(self, transcript_segments: List[Dict],
                                   image_infos: List[Dict]) -> List[Dict]:
        """
        Use AI to match images to transcript segments
        """
        print_info("Using AI to match images with transcript...")

        url = "https://api.openai.com/v1/chat/completions"

        # Prepare data for AI
        transcript_data = []
        for i, seg in enumerate(transcript_segments):
            transcript_data.append({
                "segment_id": i,
                "text": seg['text'],
                "start": seg['start'],
                "end": seg['end']
            })

        image_data = []
        for i, img in enumerate(image_infos):
            image_data.append({
                "image_id": i,
                "filename": img['filename'],
                "description": img['description'],
                "keywords": img['keywords']
            })

        prompt = f"""You are a video editor AI. Match images to transcript segments based on content relevance.

TRANSCRIPT SEGMENTS:
{json.dumps(transcript_data, indent=2)}

AVAILABLE IMAGES:
{json.dumps(image_data, indent=2)}

RULES:
1. Match each transcript segment with the MOST RELEVANT image
2. An image can be used for multiple segments if it's relevant
3. If no image matches well, use the most generic/neutral image
4. Consider: keywords, themes, emotions, settings, actions
5. Return matches sorted by transcript segment order

Return JSON array:
[
    {{"segment_id": 0, "image_id": 2, "reason": "brief reason"}},
    {{"segment_id": 1, "image_id": 0, "reason": "brief reason"}},
    ...
]

Match ALL transcript segments. Be creative in finding connections."""

        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": "You are a video editing AI that matches images to narration."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 2000,
            "temperature": 0.3
        }

        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=120)

            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']

                # Parse JSON array from response
                json_match = re.search(r'\[.*\]', content, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())

            return None

        except Exception as e:
            print_error(f"Matching error: {e}")
            return None


# ═══════════════════════════════════════════════════════════════════
# AUDIO ANALYZER
# ═══════════════════════════════════════════════════════════════════

class AudioAnalyzer:
    """Analyze audio and extract segments"""

    @staticmethod
    def get_duration(audio_path: str) -> float:
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
    def parse_transcription(transcription: Dict) -> List[Dict]:
        """
        Parse OpenAI transcription into segments with timestamps
        """
        segments = []

        # Get words with timestamps
        words = transcription.get('words', [])

        if not words:
            # Fallback: use segments if available
            for seg in transcription.get('segments', []):
                segments.append({
                    'text': seg.get('text', '').strip(),
                    'start': seg.get('start', 0),
                    'end': seg.get('end', 0)
                })
            return segments

        # Group words into sentences/phrases
        current_segment = {
            'text': '',
            'start': words[0]['start'] if words else 0,
            'end': 0,
            'words': []
        }

        for word_info in words:
            word = word_info.get('word', '')
            start = word_info.get('start', 0)
            end = word_info.get('end', 0)

            current_segment['text'] += word + ' '
            current_segment['end'] = end
            current_segment['words'].append({
                'word': word,
                'start': start,
                'end': end
            })

            # Check for sentence end
            if any(word.rstrip().endswith(p) for p in ['.', '!', '?', ',', ';', ':']):
                # Check minimum segment duration (at least 2 seconds)
                if current_segment['end'] - current_segment['start'] >= 2.0:
                    current_segment['text'] = current_segment['text'].strip()
                    segments.append(current_segment)

                    # Start new segment
                    current_segment = {
                        'text': '',
                        'start': end,
                        'end': 0,
                        'words': []
                    }

        # Add remaining segment
        if current_segment['text'].strip():
            current_segment['text'] = current_segment['text'].strip()
            segments.append(current_segment)

        return segments


# ═══════════════════════════════════════════════════════════════════
# IMAGE ANALYZER
# ═══════════════════════════════════════════════════════════════════

class ImageAnalyzer:
    """Analyze images and extract content information"""

    @staticmethod
    def get_image_files(folder: str) -> List[str]:
        valid_ext = {'.jpg', '.jpeg', '.png', '.webp', '.bmp', '.gif'}
        images = []
        for f in sorted(os.listdir(folder)):
            if os.path.splitext(f)[1].lower() in valid_ext:
                images.append(os.path.join(folder, f))
        return images

    @staticmethod
    def analyze_all_images(images: List[str], openai_client: OpenAIClient,
                          progress_callback=None) -> List[Dict]:
        """
        Analyze all images using AI vision
        """
        results = []

        for i, img_path in enumerate(images):
            if progress_callback:
                progress_callback(i, len(images))

            analysis = openai_client.analyze_image(img_path)

            if analysis:
                results.append({
                    'path': img_path,
                    'filename': os.path.basename(img_path),
                    'description': analysis.get('description', 'Unknown'),
                    'keywords': analysis.get('keywords', [])
                })
            else:
                # Fallback: use filename as description
                results.append({
                    'path': img_path,
                    'filename': os.path.basename(img_path),
                    'description': os.path.splitext(os.path.basename(img_path))[0],
                    'keywords': []
                })

            time.sleep(0.5)  # Rate limiting

        if progress_callback:
            progress_callback(len(images), len(images))

        return results


# ═══════════════════════════════════════════════════════════════════
# VIDEO GENERATOR
# ═══════════════════════════════════════════════════════════════════

class VideoGenerator:
    """Generate video with intelligent sync"""

    @staticmethod
    def create_video(video_segments: List[Dict], audio_path: str,
                    output_path: str, resolution: str = "1920x1080") -> bool:
        """
        Create video from matched segments
        """
        if not video_segments:
            print_error("No video segments!")
            return False

        width, height = map(int, resolution.split('x'))

        # Create concat file
        concat_file = Path(output_path).parent / "concat.txt"

        with open(concat_file, 'w') as f:
            for seg in video_segments:
                duration = seg['end'] - seg['start']
                if duration < 0.1:
                    duration = 2.0

                f.write(f"file '{seg['image_path']}'\n")
                f.write(f"duration {duration:.6f}\n")

            # Add last image (FFmpeg requirement)
            f.write(f"file '{video_segments[-1]['image_path']}'\n")

        # FFmpeg command
        cmd = [
            'ffmpeg', '-y',
            '-f', 'concat', '-safe', '0',
            '-i', str(concat_file),
            '-i', audio_path,
            '-vf', f'scale={width}:{height}:force_original_aspect_ratio=decrease,'
                   f'pad={width}:{height}:(ow-iw)/2:(oh-ih)/2:black',
            '-c:v', 'libx264', '-preset', 'medium', '-crf', '18',
            '-pix_fmt', 'yuv420p',
            '-c:a', 'aac', '-b:a', '192k',
            '-shortest',
            '-movflags', '+faststart',
            output_path
        ]

        print_info("Creating video with FFmpeg...")
        result = subprocess.run(cmd, capture_output=True, text=True)

        concat_file.unlink(missing_ok=True)

        return result.returncode == 0


# ═══════════════════════════════════════════════════════════════════
# INTELLIGENT SYNC ENGINE
# ═══════════════════════════════════════════════════════════════════

class IntelligentSyncEngine:
    """Main engine for intelligent voice-image synchronization"""

    def __init__(self, openai_api_key: str):
        self.openai = OpenAIClient(openai_api_key)

    def process(self, audio_path: str, images_folder: str,
               output_path: str, resolution: str = "1920x1080") -> Tuple[bool, Dict]:
        """
        Main processing pipeline:
        1. Transcribe audio (word-by-word)
        2. Analyze each image (AI vision)
        3. Match images to transcript (AI matching)
        4. Create synced video
        """

        results = {
            'audio_duration': 0,
            'total_images': 0,
            'used_images': 0,
            'segments': 0
        }

        # ═══════════════════════════════════════════════════════════
        # STEP 1: AUDIO TRANSCRIPTION
        # ═══════════════════════════════════════════════════════════
        print_step(1, "AUDIO ANALYSIS - Transcribing word by word...")

        duration = AudioAnalyzer.get_duration(audio_path)
        results['audio_duration'] = duration
        print_info(f"Audio duration: {format_time(duration)}")

        transcription = self.openai.transcribe_audio(audio_path)

        if not transcription:
            print_error("Failed to transcribe audio!")
            return False, results

        print_success(f"Transcription complete!")
        print_info(f"Full text: {transcription.get('text', '')[:200]}...")

        # Parse into segments
        segments = AudioAnalyzer.parse_transcription(transcription)
        results['segments'] = len(segments)

        print_success(f"Created {len(segments)} transcript segments")

        # Show sample segments
        print(f"\n{Colors.CYAN}Sample segments:{Colors.END}")
        for i, seg in enumerate(segments[:3]):
            print(f"  [{format_time(seg['start'])} - {format_time(seg['end'])}] {seg['text'][:60]}...")
        if len(segments) > 3:
            print(f"  ... and {len(segments) - 3} more segments")

        # ═══════════════════════════════════════════════════════════
        # STEP 2: IMAGE ANALYSIS
        # ═══════════════════════════════════════════════════════════
        print_step(2, "IMAGE ANALYSIS - Understanding each image...")

        images = ImageAnalyzer.get_image_files(images_folder)
        results['total_images'] = len(images)

        if not images:
            print_error("No images found!")
            return False, results

        print_info(f"Found {len(images)} images to analyze")

        image_infos = ImageAnalyzer.analyze_all_images(
            images, self.openai,
            progress_callback=lambda c, t: progress_bar(c, t, "Analyzing images")
        )

        print_success("Image analysis complete!")

        # Show sample image descriptions
        print(f"\n{Colors.CYAN}Image descriptions:{Colors.END}")
        for img in image_infos[:3]:
            print(f"  📷 {img['filename']}: {img['description'][:60]}...")
            print(f"     Keywords: {', '.join(img['keywords'][:5])}")
        if len(image_infos) > 3:
            print(f"  ... and {len(image_infos) - 3} more images")

        # ═══════════════════════════════════════════════════════════
        # STEP 3: INTELLIGENT MATCHING
        # ═══════════════════════════════════════════════════════════
        print_step(3, "SMART MATCHING - Matching images to narration...")

        matches = self.openai.match_images_to_transcript(segments, image_infos)

        if not matches:
            print_warning("AI matching failed, using sequential fallback...")
            matches = self._fallback_matching(segments, image_infos)

        print_success(f"Created {len(matches)} matches!")

        # Track used images
        used_image_ids = set()

        # Build video segments
        video_segments = []

        for match in matches:
            seg_id = match['segment_id']
            img_id = match['image_id']

            if seg_id < len(segments) and img_id < len(image_infos):
                segment = segments[seg_id]
                image = image_infos[img_id]

                video_segments.append({
                    'image_path': image['path'],
                    'start': segment['start'],
                    'end': segment['end'],
                    'transcript': segment['text'],
                    'reason': match.get('reason', '')
                })

                used_image_ids.add(img_id)

        results['used_images'] = len(used_image_ids)

        # Show matching results
        print(f"\n{Colors.CYAN}Matching results:{Colors.END}")
        print(f"  Total images: {len(image_infos)}")
        print(f"  Images used: {len(used_image_ids)}")
        print(f"  Images skipped: {len(image_infos) - len(used_image_ids)}")

        print(f"\n{Colors.CYAN}Sample matches:{Colors.END}")
        for vs in video_segments[:3]:
            print(f"  [{format_time(vs['start'])}] \"{vs['transcript'][:40]}...\"")
            print(f"      → {os.path.basename(vs['image_path'])}")
            if vs['reason']:
                print(f"      Reason: {vs['reason'][:50]}")

        # ═══════════════════════════════════════════════════════════
        # STEP 4: VIDEO CREATION
        # ═══════════════════════════════════════════════════════════
        print_step(4, "VIDEO CREATION - Building synced video...")

        success = VideoGenerator.create_video(
            video_segments, audio_path, output_path, resolution
        )

        if success:
            file_size = os.path.getsize(output_path) / (1024 * 1024)
            results['file_size_mb'] = file_size
            print_success("Video created successfully!")

        return success, results

    def _fallback_matching(self, segments: List[Dict],
                          image_infos: List[Dict]) -> List[Dict]:
        """Fallback: distribute images evenly across segments"""
        matches = []
        num_images = len(image_infos)

        for i, seg in enumerate(segments):
            img_idx = i % num_images
            matches.append({
                'segment_id': i,
                'image_id': img_idx,
                'reason': 'Sequential fallback'
            })

        return matches


# ═══════════════════════════════════════════════════════════════════
# MAIN APPLICATION
# ═══════════════════════════════════════════════════════════════════

class AIVideoStudio:
    """Main Application"""

    def __init__(self):
        ensure_dirs()
        self.config = load_config()

    def main_menu(self):
        while True:
            print_header()
            print(f"""
{Colors.BOLD}╔══════════════════════ MAIN MENU ══════════════════════╗{Colors.END}
║                                                         ║
║  {Colors.CYAN}[1]{Colors.END} 🧠 {Colors.BOLD}INTELLIGENT SYNC VIDEO{Colors.END}                       ║
║      {Colors.YELLOW}→ AI analyzes your audio (word by word){Colors.END}          ║
║      {Colors.YELLOW}→ AI understands each image content{Colors.END}              ║
║      {Colors.YELLOW}→ Auto-matches images with narration{Colors.END}             ║
║      {Colors.YELLOW}→ Skips unused images automatically{Colors.END}              ║
║                                                         ║
║  {Colors.CYAN}[2]{Colors.END} ⚙️  Settings                                      ║
║  {Colors.CYAN}[3]{Colors.END} 🔑 API Configuration                             ║
║  {Colors.CYAN}[4]{Colors.END} 📁 Project Manager                               ║
║  {Colors.CYAN}[5]{Colors.END} 📖 Help                                          ║
║  {Colors.CYAN}[0]{Colors.END} 🚪 Exit                                          ║
║                                                         ║
╚═════════════════════════════════════════════════════════╝
""")
            choice = input(f"{Colors.YELLOW}Enter choice: {Colors.END}").strip()

            if choice == '1':
                self.intelligent_sync()
            elif choice == '2':
                self.settings_menu()
            elif choice == '3':
                self.api_configuration()
            elif choice == '4':
                self.project_manager()
            elif choice == '5':
                self.show_help()
            elif choice == '0':
                print_info("Goodbye!")
                sys.exit(0)

    # ═══════════════════════════════════════════════════════════════
    # INTELLIGENT SYNC FEATURE
    # ═══════════════════════════════════════════════════════════════

    def intelligent_sync(self):
        """Create video with intelligent voice-image sync"""
        print_header()
        print(f"""
{Colors.BOLD}╔══════════════════════════════════════════════════════════════════╗
║                    INTELLIGENT SYNC VIDEO                        ║
║              AI-Powered Voice + Image Matching                   ║
╠══════════════════════════════════════════════════════════════════╣
║  HOW IT WORKS:                                                   ║
║  1. AI transcribes your audio → understands every word          ║
║  2. AI analyzes each image → understands what's shown           ║
║  3. AI matches images to words → right image at right time      ║
║  4. Unused images are automatically skipped                      ║
╚══════════════════════════════════════════════════════════════════╝{Colors.END}
""")

        # Check API key
        openai_key = self.config["api_keys"].get("openai", "")
        if not openai_key:
            print_error("OpenAI API key required for intelligent sync!")
            print_info("Go to [3] API Configuration to add your key")
            print_info("Get key from: https://platform.openai.com/api-keys")
            input("\nPress Enter to continue...")
            return

        # Get audio file
        print(f"\n{Colors.CYAN}AUDIO FILE:{Colors.END}")
        print("Enter path to your audio file (MP3, WAV, M4A):")
        audio_path = input(f"{Colors.YELLOW}Audio: {Colors.END}").strip().strip('"\'')

        if not os.path.isfile(audio_path):
            print_error("Audio file not found!")
            input("\nPress Enter to continue...")
            return

        duration = AudioAnalyzer.get_duration(audio_path)
        print_success(f"Audio loaded: {format_time(duration)}")

        # Get images folder
        print(f"\n{Colors.CYAN}IMAGES FOLDER:{Colors.END}")
        print("Enter path to folder containing your images:")
        images_folder = input(f"{Colors.YELLOW}Folder: {Colors.END}").strip().strip('"\'')

        if not os.path.isdir(images_folder):
            print_error("Folder not found!")
            input("\nPress Enter to continue...")
            return

        images = ImageAnalyzer.get_image_files(images_folder)
        if not images:
            print_error("No images found!")
            input("\nPress Enter to continue...")
            return

        print_success(f"Found {len(images)} images")

        # Create project
        project_name = f"intelligent_sync_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        project_dir = PROJECTS_DIR / project_name
        project_dir.mkdir(parents=True, exist_ok=True)

        output_path = str(project_dir / "final_video.mp4")
        resolution = self.config["settings"].get("video_resolution", "1920x1080")

        # Confirm
        print(f"""
{Colors.BOLD}╔═══════════════════ SUMMARY ═══════════════════╗{Colors.END}
  Audio: {os.path.basename(audio_path)}
  Duration: {format_time(duration)}
  Images: {len(images)} files
  Resolution: {resolution}

  {Colors.YELLOW}AI will:{Colors.END}
  ✓ Transcribe audio word-by-word
  ✓ Analyze what's in each image
  ✓ Match images to narration content
  ✓ Skip irrelevant images
{Colors.BOLD}╚═══════════════════════════════════════════════╝{Colors.END}
""")

        confirm = input(f"{Colors.YELLOW}Start intelligent sync? (Y/n): {Colors.END}").strip().lower()
        if confirm == 'n':
            return

        # Process
        print(f"\n{Colors.CYAN}{'═' * 60}{Colors.END}")
        print(f"{Colors.BOLD}Starting Intelligent Sync Process...{Colors.END}")
        print(f"{Colors.CYAN}{'═' * 60}{Colors.END}")

        engine = IntelligentSyncEngine(openai_key)
        success, results = engine.process(
            audio_path=audio_path,
            images_folder=images_folder,
            output_path=output_path,
            resolution=resolution
        )

        if success:
            print(f"""
{Colors.GREEN}╔══════════════════════════════════════════════════════════════════╗
║                    VIDEO CREATED SUCCESSFULLY!                   ║
╠══════════════════════════════════════════════════════════════════╣
║  📁 Output: {output_path[:50]}...
║  ⏱️  Duration: {format_time(results['audio_duration'])}
║  📊 Size: {results.get('file_size_mb', 0):.1f} MB
║  🖼️  Total Images: {results['total_images']}
║  ✓  Images Used: {results['used_images']}
║  ✗  Images Skipped: {results['total_images'] - results['used_images']}
║  📝 Segments: {results['segments']}
╚══════════════════════════════════════════════════════════════════╝{Colors.END}
""")
        else:
            print_error("Video creation failed!")

        input("\nPress Enter to continue...")

    # ═══════════════════════════════════════════════════════════════
    # OTHER MENUS
    # ═══════════════════════════════════════════════════════════════

    def settings_menu(self):
        while True:
            print_header()
            print(f"""
{Colors.BOLD}╔═══════════════ SETTINGS ═══════════════╗{Colors.END}

  {Colors.CYAN}[1]{Colors.END} Video Resolution: {self.config['settings']['video_resolution']}

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
            elif choice == '0':
                break

    def api_configuration(self):
        print_header()
        print(f"""
{Colors.BOLD}╔═══════════════ API CONFIGURATION ═══════════════╗{Colors.END}

{Colors.YELLOW}Required for Intelligent Sync:{Colors.END}
  - OpenAI API Key (for transcription + vision)

{Colors.CYAN}Get your key from:{Colors.END}
  https://platform.openai.com/api-keys

""")

        current = self.config["api_keys"].get("openai", "")
        display = current[:20] + "..." if current else "Not set"
        print(f"{Colors.CYAN}OpenAI API Key{Colors.END} [{display}]")
        new_val = input("Enter new key (or press Enter to skip): ").strip()
        if new_val:
            self.config["api_keys"]["openai"] = new_val
            save_config(self.config)
            print_success("API key saved!")

        input("\nPress Enter to continue...")

    def project_manager(self):
        print_header()
        print(f"{Colors.BOLD}╔═══════════ PROJECT MANAGER ═══════════╗{Colors.END}\n")

        projects = [p for p in PROJECTS_DIR.iterdir() if p.is_dir()] if PROJECTS_DIR.exists() else []

        if not projects:
            print_info("No projects found.")
            input("\nPress Enter to continue...")
            return

        for i, p in enumerate(sorted(projects), 1):
            size = sum(f.stat().st_size for f in p.rglob('*') if f.is_file())
            print(f"  [{i}] {p.name} ({size/1024/1024:.1f} MB)")

        print(f"\n  [O] Open  [D] Delete  [B] Back")
        choice = input("Choice: ").strip().upper()

        if choice == 'O':
            idx = input("Number: ").strip()
            if idx.isdigit() and 1 <= int(idx) <= len(projects):
                p = sorted(projects)[int(idx)-1]
                os.startfile(p) if os.name == 'nt' else subprocess.run(['xdg-open', str(p)])
        elif choice == 'D':
            idx = input("Number to delete: ").strip()
            if idx.isdigit() and 1 <= int(idx) <= len(projects):
                if input("Confirm delete? (y/N): ").lower() == 'y':
                    shutil.rmtree(sorted(projects)[int(idx)-1])
                    print_success("Deleted!")

        input("\nPress Enter to continue...")

    def show_help(self):
        print_header()
        print(f"""
{Colors.BOLD}╔═══════════════════════ HELP ═══════════════════════╗{Colors.END}

{Colors.CYAN}INTELLIGENT SYNC - How it works:{Colors.END}

  {Colors.BOLD}Step 1: Audio Analysis{Colors.END}
  - AI listens to your audio file
  - Transcribes every word with precise timestamps
  - Creates segments based on sentences

  {Colors.BOLD}Step 2: Image Analysis{Colors.END}
  - AI looks at each image using computer vision
  - Understands what's shown: objects, people, scenes
  - Creates keywords and descriptions

  {Colors.BOLD}Step 3: Smart Matching{Colors.END}
  - AI matches images to narration content
  - Example: Words about "sunset" → beach sunset image
  - Irrelevant images are automatically skipped

  {Colors.BOLD}Step 4: Video Creation{Colors.END}
  - Creates perfectly synced video
  - Right image appears at right time

{Colors.CYAN}REQUIREMENTS:{Colors.END}
  - OpenAI API Key (for AI features)
  - FFmpeg (for video creation)
  - Python 3.8+

{Colors.CYAN}GET OPENAI API KEY:{Colors.END}
  https://platform.openai.com/api-keys

╚═════════════════════════════════════════════════════╝
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
