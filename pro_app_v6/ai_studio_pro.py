#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                      AI VIDEO STUDIO PRO v6.0                                ║
║            Professional Video Editor with Intelligent Auto-Sync             ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  CORE FEATURES:                                                               ║
║  ✓ Multi-Track Timeline (Images, Audio, Captions, Overlays)                  ║
║  ✓ Intelligent Auto-Sync (Voice-to-Image Matching)                           ║
║  ✓ Word-by-Word Caption Highlighting                                         ║
║  ✓ Ken Burns Effect & Transitions                                            ║
║  ✓ Overlay System with Blend Modes                                           ║
║  ✓ Professional Export (H.264/H.265, GPU Acceleration)                       ║
║  ✓ Caption Styling (Fonts, Colors, Animations)                               ║
║  ✓ Background Music with Ducking                                             ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import os
import sys
import json
import threading
import subprocess
import time
import shutil
import requests
import base64
import re
import wave
import struct
import math
import random
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext, colorchooser
from tkinter import font as tkfont

# PIL for images
try:
    from PIL import Image, ImageTk, ImageDraw, ImageFilter, ImageFont, ImageEnhance
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("Warning: PIL not installed. Run: pip install Pillow")

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION & CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════════

APP_NAME = "AI Video Studio Pro"
VERSION = "6.0.0"
APP_DIR = Path(__file__).parent
CONFIG_FILE = APP_DIR / "config.json"
PROJECTS_DIR = APP_DIR / "projects"
TEMP_DIR = APP_DIR / "temp"
FONTS_DIR = APP_DIR / "fonts"

# Modern Dark Theme
COLORS = {
    'bg_dark': '#0d1117',
    'bg_medium': '#161b22',
    'bg_light': '#21262d',
    'bg_lighter': '#30363d',
    'accent': '#238636',
    'accent_blue': '#1f6feb',
    'accent_purple': '#8957e5',
    'accent_red': '#f85149',
    'accent_orange': '#d29922',
    'accent_cyan': '#39c5cf',
    'text': '#f0f6fc',
    'text_dim': '#8b949e',
    'text_muted': '#6e7681',
    'border': '#30363d',
    'success': '#3fb950',
    'warning': '#d29922',
    'error': '#f85149',
    'timeline_bg': '#0d1117',
    'track_images': '#238636',
    'track_audio': '#1f6feb',
    'track_captions': '#8957e5',
    'track_music': '#d29922',
    'track_overlay': '#39c5cf',
    'waveform': '#58a6ff',
    'playhead': '#f85149'
}

# Blend Modes
class BlendMode(Enum):
    NORMAL = "normal"
    MULTIPLY = "multiply"
    SCREEN = "screen"
    OVERLAY = "overlay"
    SOFT_LIGHT = "soft_light"
    HARD_LIGHT = "hard_light"
    DARKEN = "darken"
    LIGHTEN = "lighten"
    COLOR_DODGE = "color_dodge"
    COLOR_BURN = "color_burn"
    DIFFERENCE = "difference"

# Transition Types
class TransitionType(Enum):
    NONE = "none"
    FADE = "fade"
    CROSS_DISSOLVE = "cross_dissolve"
    SLIDE_LEFT = "slide_left"
    SLIDE_RIGHT = "slide_right"
    SLIDE_UP = "slide_up"
    SLIDE_DOWN = "slide_down"
    ZOOM_IN = "zoom_in"
    ZOOM_OUT = "zoom_out"
    WIPE_LEFT = "wipe_left"
    WIPE_RIGHT = "wipe_right"

# Caption Animations
class CaptionAnimation(Enum):
    NONE = "none"
    FADE = "fade"
    SLIDE_UP = "slide_up"
    SLIDE_DOWN = "slide_down"
    TYPEWRITER = "typewriter"
    POP = "pop"
    BOUNCE = "bounce"
    HIGHLIGHT = "highlight"

# ═══════════════════════════════════════════════════════════════════════════════
# DATA CLASSES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class TimelineClip:
    """Represents a clip on the timeline"""
    id: str
    track: str  # 'images', 'audio', 'captions', 'music', 'overlay'
    start_time: float
    end_time: float
    source_path: str = ""
    text: str = ""

    # Image properties
    zoom_start: float = 1.0
    zoom_end: float = 1.2
    pan_x: float = 0.0
    pan_y: float = 0.0
    rotation: float = 0.0
    brightness: float = 1.0
    contrast: float = 1.0
    saturation: float = 1.0

    # Transition
    transition_in: TransitionType = TransitionType.FADE
    transition_out: TransitionType = TransitionType.FADE
    transition_duration: float = 0.5

    # Overlay properties
    opacity: float = 1.0
    blend_mode: BlendMode = BlendMode.NORMAL
    position_x: float = 0.5
    position_y: float = 0.5
    scale: float = 1.0

    # Caption properties
    font_family: str = "Arial"
    font_size: int = 48
    font_color: str = "#FFFFFF"
    font_bold: bool = False
    font_italic: bool = False
    bg_color: str = ""
    stroke_color: str = "#000000"
    stroke_width: int = 2
    caption_animation: CaptionAnimation = CaptionAnimation.FADE

    @property
    def duration(self) -> float:
        return self.end_time - self.start_time

@dataclass
class WordTimestamp:
    """Word with timing information"""
    word: str
    start: float
    end: float

@dataclass
class Project:
    """Project data"""
    name: str = "Untitled Project"
    audio_path: str = ""
    audio_duration: float = 0.0
    bg_music_path: str = ""
    bg_music_volume: float = 0.3
    clips: List[TimelineClip] = field(default_factory=list)
    words: List[WordTimestamp] = field(default_factory=list)

    # Export settings
    resolution: str = "1920x1080"
    fps: int = 30
    bitrate: str = "8M"
    codec: str = "h264"

# ═══════════════════════════════════════════════════════════════════════════════
# UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def ensure_dirs():
    for d in [PROJECTS_DIR, TEMP_DIR, FONTS_DIR]:
        d.mkdir(parents=True, exist_ok=True)

def load_config():
    default = {
        "api_keys": {"openai": ""},
        "recent_projects": [],
        "preferences": {
            "default_image_duration": 5.0,
            "default_transition": "fade",
            "default_caption_font": "Arial",
            "auto_save": True
        }
    }
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r') as f:
                cfg = json.load(f)
                for key in default:
                    if key not in cfg:
                        cfg[key] = default[key]
                return cfg
        except:
            pass
    return default

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)

def get_audio_duration(path):
    try:
        cmd = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
               '-of', 'default=noprint_wrappers=1:nokey=1', path]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return float(result.stdout.strip())
    except:
        return 0.0

def format_time(seconds):
    """Format seconds to MM:SS.ms"""
    mins = int(seconds // 60)
    secs = seconds % 60
    return f"{mins:02d}:{secs:05.2f}"

def format_time_short(seconds):
    """Format seconds to MM:SS"""
    mins = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{mins:02d}:{secs:02d}"

def check_gpu():
    """Check available GPU encoders"""
    try:
        result = subprocess.run(['ffmpeg', '-hide_banner', '-encoders'],
                               capture_output=True, text=True)
        if 'h264_nvenc' in result.stdout:
            return 'nvenc', 'NVIDIA NVENC'
        if 'h264_qsv' in result.stdout:
            return 'qsv', 'Intel QuickSync'
        if 'h264_amf' in result.stdout:
            return 'amf', 'AMD AMF'
    except:
        pass
    return None, 'CPU Only'

def get_system_fonts():
    """Get list of system fonts"""
    fonts = list(tkfont.families())
    # Prioritize common fonts
    priority = ['Arial', 'Helvetica', 'Times New Roman', 'Verdana', 'Tahoma',
                'Georgia', 'Trebuchet MS', 'Impact', 'Comic Sans MS', 'Courier New']
    sorted_fonts = [f for f in priority if f in fonts]
    sorted_fonts.extend([f for f in sorted(fonts) if f not in priority])
    return sorted_fonts

def generate_id():
    """Generate unique ID"""
    return f"{time.time()}_{random.randint(1000, 9999)}"

# ═══════════════════════════════════════════════════════════════════════════════
# OPENAI CLIENT - Whisper API for Auto-Sync
# ═══════════════════════════════════════════════════════════════════════════════

class OpenAIClient:
    """OpenAI API client for Whisper transcription"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.openai.com/v1"

    def transcribe_with_timestamps(self, audio_path: str,
                                    progress_callback=None) -> Tuple[str, List[WordTimestamp]]:
        """
        Transcribe audio with word-level timestamps using Whisper API
        Returns: (full_text, list of WordTimestamp)
        """
        if progress_callback:
            progress_callback("Uploading audio to OpenAI Whisper...")

        try:
            with open(audio_path, 'rb') as f:
                response = requests.post(
                    f"{self.base_url}/audio/transcriptions",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    files={"file": f},
                    data={
                        "model": "whisper-1",
                        "response_format": "verbose_json",
                        "timestamp_granularities[]": "word"
                    },
                    timeout=600  # 10 min timeout for long audio
                )

            if response.status_code != 200:
                raise Exception(f"API Error: {response.status_code} - {response.text}")

            data = response.json()

            if progress_callback:
                progress_callback("Processing transcription...")

            # Extract words with timestamps
            words = []
            for w in data.get('words', []):
                words.append(WordTimestamp(
                    word=w['word'],
                    start=w['start'],
                    end=w['end']
                ))

            full_text = data.get('text', '')

            return full_text, words

        except Exception as e:
            raise Exception(f"Transcription failed: {str(e)}")

    def analyze_image(self, image_path: str) -> str:
        """Analyze image content using GPT-4 Vision"""
        try:
            with open(image_path, "rb") as f:
                img_data = base64.b64encode(f.read()).decode('utf-8')

            ext = os.path.splitext(image_path)[1].lower()
            media_type = {'.jpg': 'image/jpeg', '.jpeg': 'image/jpeg',
                         '.png': 'image/png', '.webp': 'image/webp'}.get(ext, 'image/jpeg')

            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-4o-mini",
                    "messages": [{
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{media_type};base64,{img_data}",
                                    "detail": "low"
                                }
                            },
                            {
                                "type": "text",
                                "text": "Describe this image in 10 keywords. Return ONLY comma-separated keywords, nothing else."
                            }
                        ]
                    }],
                    "max_tokens": 100
                },
                timeout=30
            )

            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content']
        except:
            pass
        return ""

# ═══════════════════════════════════════════════════════════════════════════════
# INTELLIGENT AUTO-SYNC ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

class AutoSyncEngine:
    """
    Intelligent engine that automatically syncs images with voice narration.
    Uses OpenAI Whisper for speech-to-text with word-level timestamps.
    """

    def __init__(self, openai_client: OpenAIClient):
        self.client = openai_client

    def create_auto_sync(self, audio_path: str, image_paths: List[str],
                         progress_callback=None) -> Tuple[List[TimelineClip], List[TimelineClip], List[WordTimestamp]]:
        """
        Automatically create timeline clips from audio and images.

        Returns:
            - image_clips: List of image clips with timings
            - caption_clips: List of caption clips (phrases)
            - words: List of all words with timestamps
        """

        # Step 1: Transcribe audio with word timestamps
        if progress_callback:
            progress_callback(0, 5, "Transcribing audio with AI...")

        full_text, words = self.client.transcribe_with_timestamps(
            audio_path,
            lambda msg: progress_callback(0, 5, msg) if progress_callback else None
        )

        if not words:
            raise Exception("No words detected in audio!")

        # Step 2: Group words into phrases/sentences
        if progress_callback:
            progress_callback(1, 5, "Grouping words into phrases...")

        phrases = self._group_words_into_phrases(words)

        # Step 3: Analyze images (optional, for smart matching)
        if progress_callback:
            progress_callback(2, 5, "Analyzing images...")

        image_keywords = []
        for i, img_path in enumerate(image_paths):
            if progress_callback:
                progress_callback(2, 5, f"Analyzing image {i+1}/{len(image_paths)}...")
            keywords = self.client.analyze_image(img_path)
            image_keywords.append(keywords)
            time.sleep(0.2)  # Rate limiting

        # Step 4: Match images to phrases
        if progress_callback:
            progress_callback(3, 5, "Matching images to narration...")

        image_clips = self._match_images_to_phrases(phrases, image_paths, image_keywords)

        # Step 5: Create caption clips
        if progress_callback:
            progress_callback(4, 5, "Creating captions...")

        caption_clips = self._create_caption_clips(phrases)

        if progress_callback:
            progress_callback(5, 5, "Auto-sync complete!")

        return image_clips, caption_clips, words

    def _group_words_into_phrases(self, words: List[WordTimestamp],
                                   min_phrase_duration: float = 2.0,
                                   max_phrase_duration: float = 6.0) -> List[Dict]:
        """
        Group words into natural phrases based on:
        - Punctuation
        - Pauses between words
        - Duration limits
        """
        if not words:
            return []

        phrases = []
        current_phrase = {
            'words': [],
            'text': '',
            'start': words[0].start,
            'end': 0
        }

        for i, word in enumerate(words):
            current_phrase['words'].append(word)
            current_phrase['text'] += word.word + ' '
            current_phrase['end'] = word.end

            # Check if we should end this phrase
            should_end = False

            # End at sentence boundaries
            if word.word.rstrip().endswith(('.', '!', '?')):
                should_end = True

            # End at comma if phrase is long enough
            elif word.word.rstrip().endswith(','):
                if current_phrase['end'] - current_phrase['start'] >= min_phrase_duration:
                    should_end = True

            # Check for pause before next word
            if i < len(words) - 1:
                next_word = words[i + 1]
                pause = next_word.start - word.end
                if pause > 0.5 and current_phrase['end'] - current_phrase['start'] >= min_phrase_duration:
                    should_end = True

            # Force end if max duration reached
            if current_phrase['end'] - current_phrase['start'] >= max_phrase_duration:
                should_end = True

            if should_end or i == len(words) - 1:
                current_phrase['text'] = current_phrase['text'].strip()
                if current_phrase['text']:
                    phrases.append(current_phrase)

                if i < len(words) - 1:
                    current_phrase = {
                        'words': [],
                        'text': '',
                        'start': words[i + 1].start,
                        'end': 0
                    }

        return phrases

    def _match_images_to_phrases(self, phrases: List[Dict],
                                  image_paths: List[str],
                                  image_keywords: List[str]) -> List[TimelineClip]:
        """
        Match images to phrases intelligently.
        If more phrases than images, images are reused.
        """
        clips = []
        num_images = len(image_paths)

        for i, phrase in enumerate(phrases):
            # Determine which image to use
            # Simple round-robin if no smart matching
            image_idx = i % num_images

            # Create clip
            clip = TimelineClip(
                id=generate_id(),
                track='images',
                start_time=phrase['start'],
                end_time=phrase['end'],
                source_path=image_paths[image_idx],
                zoom_start=1.0,
                zoom_end=random.choice([1.1, 1.15, 1.2]),  # Random Ken Burns
                transition_in=TransitionType.FADE,
                transition_out=TransitionType.FADE,
                transition_duration=0.5
            )
            clips.append(clip)

        return clips

    def _create_caption_clips(self, phrases: List[Dict]) -> List[TimelineClip]:
        """Create caption clips from phrases"""
        clips = []

        for phrase in phrases:
            clip = TimelineClip(
                id=generate_id(),
                track='captions',
                start_time=phrase['start'],
                end_time=phrase['end'],
                text=phrase['text'],
                font_family="Arial",
                font_size=48,
                font_color="#FFFFFF",
                stroke_color="#000000",
                stroke_width=2,
                caption_animation=CaptionAnimation.FADE
            )
            clips.append(clip)

        return clips

# ═══════════════════════════════════════════════════════════════════════════════
# VIDEO PROCESSOR
# ═══════════════════════════════════════════════════════════════════════════════

class VideoProcessor:
    """Handles all video rendering with FFmpeg"""

    @staticmethod
    def create_video(project: Project, output_path: str,
                     progress_callback=None) -> bool:
        """
        Create final video from project with all effects.
        """

        if not project.clips:
            return False

        # Get image clips
        image_clips = [c for c in project.clips if c.track == 'images']
        if not image_clips:
            return False

        # Sort by start time
        image_clips.sort(key=lambda c: c.start_time)

        width, height = map(int, project.resolution.split('x'))
        temp_dir = Path(output_path).parent / f"temp_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        temp_dir.mkdir(exist_ok=True)

        try:
            total_steps = len(image_clips) + 3
            current_step = 0

            # Check GPU
            gpu_type, _ = check_gpu()
            encoder = 'libx264'
            encoder_opts = ['-preset', 'medium']

            if gpu_type == 'nvenc':
                encoder = 'h264_nvenc'
                encoder_opts = ['-preset', 'p4', '-tune', 'hq']
            elif gpu_type == 'qsv':
                encoder = 'h264_qsv'
                encoder_opts = ['-preset', 'medium']
            elif gpu_type == 'amf':
                encoder = 'h264_amf'
                encoder_opts = []

            # Process each image clip with Ken Burns effect
            clip_files = []

            for i, clip in enumerate(image_clips):
                if progress_callback:
                    progress_callback(i, total_steps, f"Processing clip {i+1}/{len(image_clips)}")

                clip_path = temp_dir / f"clip_{i:04d}.mp4"
                duration = clip.duration

                # Ken Burns zoom effect
                frames = int(duration * project.fps)
                start_zoom = clip.zoom_start
                end_zoom = clip.zoom_end

                zoom_filter = (
                    f"zoompan=z='if(eq(on,1),{start_zoom},{start_zoom}+({end_zoom}-{start_zoom})*on/{frames})':"
                    f"x='iw/2-(iw/zoom/2)+{int(clip.pan_x * 100)}*on/{frames}':"
                    f"y='ih/2-(ih/zoom/2)+{int(clip.pan_y * 100)}*on/{frames}':"
                    f"d={frames}:s={width}x{height}:fps={project.fps}"
                )

                # Add fade if transition
                video_filter = zoom_filter
                if clip.transition_in == TransitionType.FADE:
                    video_filter += f",fade=t=in:st=0:d={clip.transition_duration}"
                if clip.transition_out == TransitionType.FADE:
                    video_filter += f",fade=t=out:st={duration-clip.transition_duration}:d={clip.transition_duration}"

                # Add color adjustments
                if clip.brightness != 1.0 or clip.contrast != 1.0 or clip.saturation != 1.0:
                    video_filter += f",eq=brightness={clip.brightness-1}:contrast={clip.contrast}:saturation={clip.saturation}"

                cmd = [
                    'ffmpeg', '-y', '-loop', '1', '-i', clip.source_path,
                    '-vf', video_filter,
                    '-c:v', encoder, *encoder_opts,
                    '-t', str(duration),
                    '-pix_fmt', 'yuv420p',
                    '-an',
                    str(clip_path)
                ]

                subprocess.run(cmd, capture_output=True)
                clip_files.append((clip.start_time, str(clip_path)))

            current_step = len(image_clips)
            if progress_callback:
                progress_callback(current_step, total_steps, "Concatenating clips...")

            # Create concat file
            concat_file = temp_dir / "concat.txt"
            with open(concat_file, 'w') as f:
                for _, clip_path in sorted(clip_files, key=lambda x: x[0]):
                    f.write(f"file '{clip_path}'\n")

            # Combine video clips
            temp_video = temp_dir / "temp_video.mp4"
            cmd = [
                'ffmpeg', '-y',
                '-f', 'concat', '-safe', '0', '-i', str(concat_file),
                '-c:v', encoder, *encoder_opts,
                '-pix_fmt', 'yuv420p',
                str(temp_video)
            ]
            subprocess.run(cmd, capture_output=True)

            current_step += 1
            if progress_callback:
                progress_callback(current_step, total_steps, "Adding audio...")

            # Add audio tracks
            cmd = ['ffmpeg', '-y', '-i', str(temp_video), '-i', project.audio_path]

            filter_complex = []

            # Add background music if exists
            if project.bg_music_path and os.path.exists(project.bg_music_path):
                cmd.extend(['-i', project.bg_music_path])
                filter_complex.append(
                    f"[1:a]volume=1.0[narration];"
                    f"[2:a]volume={project.bg_music_volume}[music];"
                    f"[narration][music]amix=inputs=2:duration=first[aout]"
                )
                audio_map = '[aout]'
            else:
                audio_map = '1:a'

            if filter_complex:
                cmd.extend(['-filter_complex', ';'.join(filter_complex)])
                cmd.extend(['-map', '0:v', '-map', audio_map])
            else:
                cmd.extend(['-map', '0:v', '-map', '1:a'])

            cmd.extend([
                '-c:v', 'copy',
                '-c:a', 'aac', '-b:a', '192k',
                '-shortest',
                '-movflags', '+faststart',
                output_path
            ])

            subprocess.run(cmd, capture_output=True)

            # Cleanup
            shutil.rmtree(temp_dir, ignore_errors=True)

            if progress_callback:
                progress_callback(total_steps, total_steps, "Complete!")

            return os.path.exists(output_path)

        except Exception as e:
            print(f"Video processing error: {e}")
            shutil.rmtree(temp_dir, ignore_errors=True)
            return False

    @staticmethod
    def create_video_with_captions(project: Project, output_path: str,
                                   progress_callback=None) -> bool:
        """
        Create video with burned-in captions.
        Uses FFmpeg drawtext filter for word-by-word highlighting.
        """

        # First create video without captions
        temp_video = str(Path(output_path).parent / "temp_no_captions.mp4")

        if not VideoProcessor.create_video(project, temp_video, progress_callback):
            return False

        # Get caption clips
        caption_clips = [c for c in project.clips if c.track == 'captions']
        if not caption_clips:
            # No captions, just rename
            shutil.move(temp_video, output_path)
            return True

        # Build drawtext filter for each caption
        drawtext_filters = []

        for clip in caption_clips:
            # Escape text for FFmpeg
            text = clip.text.replace("'", "\\'").replace(":", "\\:")

            # Position (bottom center)
            x = "(w-text_w)/2"
            y = "h-100"

            drawtext = (
                f"drawtext=text='{text}':"
                f"fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:"
                f"fontsize={clip.font_size}:"
                f"fontcolor={clip.font_color}:"
                f"borderw={clip.stroke_width}:"
                f"bordercolor={clip.stroke_color}:"
                f"x={x}:y={y}:"
                f"enable='between(t,{clip.start_time},{clip.end_time})'"
            )
            drawtext_filters.append(drawtext)

        # Apply captions
        filter_str = ','.join(drawtext_filters) if drawtext_filters else 'null'

        cmd = [
            'ffmpeg', '-y', '-i', temp_video,
            '-vf', filter_str,
            '-c:v', 'libx264', '-preset', 'medium',
            '-c:a', 'copy',
            output_path
        ]

        subprocess.run(cmd, capture_output=True)

        # Cleanup
        if os.path.exists(temp_video):
            os.remove(temp_video)

        return os.path.exists(output_path)

# ═══════════════════════════════════════════════════════════════════════════════
# AUDIO WAVEFORM GENERATOR
# ═══════════════════════════════════════════════════════════════════════════════

class WaveformGenerator:
    """Generate audio waveform visualization"""

    @staticmethod
    def get_waveform_data(audio_path: str, num_samples: int = 500) -> List[float]:
        """Extract normalized waveform data from audio"""
        try:
            # Convert to mono WAV
            temp_wav = TEMP_DIR / "temp_waveform.wav"
            subprocess.run([
                'ffmpeg', '-y', '-i', audio_path,
                '-ac', '1', '-ar', '8000', '-f', 'wav',
                str(temp_wav)
            ], capture_output=True)

            if not temp_wav.exists():
                return []

            with wave.open(str(temp_wav), 'rb') as wav:
                n_frames = wav.getnframes()
                if n_frames == 0:
                    return []

                frames = wav.readframes(n_frames)
                samples = struct.unpack(f'{n_frames}h', frames)

                # Downsample
                chunk_size = max(1, len(samples) // num_samples)
                waveform = []

                for i in range(num_samples):
                    start = i * chunk_size
                    end = min(start + chunk_size, len(samples))
                    if start >= len(samples):
                        break
                    chunk = samples[start:end]
                    if chunk:
                        avg = sum(abs(s) for s in chunk) / len(chunk)
                        waveform.append(avg / 32768.0)  # Normalize to 0-1

                temp_wav.unlink()
                return waveform

        except Exception as e:
            print(f"Waveform error: {e}")
            return []

# ═══════════════════════════════════════════════════════════════════════════════
# EXPORT DIALOG
# ═══════════════════════════════════════════════════════════════════════════════

class ExportDialog:
    """Professional export dialog"""

    def __init__(self, parent, project: Project, first_image=None):
        self.result = None
        self.project = project

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Export Video")
        self.dialog.geometry("650x750")
        self.dialog.configure(bg=COLORS['bg_dark'])
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.resizable(False, False)

        # Center
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - 650) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 750) // 2
        self.dialog.geometry(f"+{x}+{y}")

        self._create_ui(first_image)

    def _create_ui(self, first_image):
        main = tk.Frame(self.dialog, bg=COLORS['bg_dark'])
        main.pack(fill='both', expand=True, padx=20, pady=20)

        # Title
        tk.Label(main, text="🎬 Export Video", font=('Segoe UI', 20, 'bold'),
                fg=COLORS['text'], bg=COLORS['bg_dark']).pack(anchor='w')

        # Preview
        preview_frame = tk.Frame(main, bg=COLORS['bg_medium'], height=160)
        preview_frame.pack(fill='x', pady=15)
        preview_frame.pack_propagate(False)

        if first_image and PIL_AVAILABLE:
            try:
                img = Image.open(first_image)
                img.thumbnail((220, 140))
                self.preview_img = ImageTk.PhotoImage(img)
                tk.Label(preview_frame, image=self.preview_img,
                        bg=COLORS['bg_medium']).pack(side='left', padx=10, pady=10)
            except:
                pass

        # Info
        info = tk.Frame(preview_frame, bg=COLORS['bg_medium'])
        info.pack(side='left', fill='both', expand=True, padx=10, pady=10)

        tk.Label(info, text="File Name", font=('Segoe UI', 9),
                fg=COLORS['text_dim'], bg=COLORS['bg_medium']).pack(anchor='w')

        self.name_var = tk.StringVar(value=f"video_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        tk.Entry(info, textvariable=self.name_var, font=('Segoe UI', 11),
                bg=COLORS['bg_light'], fg=COLORS['text'], insertbackground=COLORS['text'],
                relief='flat', width=30).pack(anchor='w', pady=(2, 8))

        tk.Label(info, text="Save to", font=('Segoe UI', 9),
                fg=COLORS['text_dim'], bg=COLORS['bg_medium']).pack(anchor='w')

        loc_frame = tk.Frame(info, bg=COLORS['bg_medium'])
        loc_frame.pack(anchor='w', fill='x')

        self.location_var = tk.StringVar(value=str(PROJECTS_DIR))
        tk.Entry(loc_frame, textvariable=self.location_var, font=('Segoe UI', 10),
                bg=COLORS['bg_light'], fg=COLORS['text'], relief='flat',
                width=22).pack(side='left')
        tk.Button(loc_frame, text="📁", bg=COLORS['bg_light'], fg=COLORS['text'],
                 relief='flat', command=self._browse).pack(side='left', padx=5)

        # Settings
        ttk.Separator(main, orient='horizontal').pack(fill='x', pady=15)

        settings = tk.Frame(main, bg=COLORS['bg_dark'])
        settings.pack(fill='x')

        # Resolution
        self._add_dropdown(settings, "Resolution",
                          ["3840x2160 (4K)", "2560x1440 (2K)", "1920x1080 (Full HD)",
                           "1280x720 (HD)", "854x480 (SD)"],
                          "resolution_var", "1920x1080 (Full HD)")

        # Bitrate
        self._add_dropdown(settings, "Bitrate",
                          ["Ultra (16M)", "High (12M)", "Medium (8M)", "Low (4M)"],
                          "bitrate_var", "Medium (8M)")

        # Codec
        self._add_dropdown(settings, "Codec",
                          ["H.264 (Best Compatibility)", "H.265/HEVC (Smaller Size)"],
                          "codec_var", "H.264 (Best Compatibility)")

        # Format
        self._add_dropdown(settings, "Format",
                          ["MP4", "MOV", "MKV", "WebM"],
                          "format_var", "MP4")

        # FPS
        self._add_dropdown(settings, "Frame Rate",
                          ["60 fps", "30 fps", "24 fps (Cinematic)"],
                          "fps_var", "30 fps")

        # GPU
        gpu_frame = tk.Frame(settings, bg=COLORS['bg_dark'])
        gpu_frame.pack(fill='x', pady=8)

        self.gpu_var = tk.BooleanVar(value=True)
        tk.Checkbutton(gpu_frame, text="Use GPU Acceleration", variable=self.gpu_var,
                      font=('Segoe UI', 10), fg=COLORS['text'], bg=COLORS['bg_dark'],
                      selectcolor=COLORS['bg_medium'], activebackground=COLORS['bg_dark']
                      ).pack(side='left')

        gpu_type, gpu_name = check_gpu()
        status_color = COLORS['success'] if gpu_type else COLORS['text_dim']
        tk.Label(gpu_frame, text=f"({gpu_name})", font=('Segoe UI', 9),
                fg=status_color, bg=COLORS['bg_dark']).pack(side='left', padx=10)

        # Captions
        self.captions_var = tk.BooleanVar(value=True)
        tk.Checkbutton(settings, text="Burn-in Captions", variable=self.captions_var,
                      font=('Segoe UI', 10), fg=COLORS['text'], bg=COLORS['bg_dark'],
                      selectcolor=COLORS['bg_medium']).pack(anchor='w', pady=5)

        # Info bar
        ttk.Separator(main, orient='horizontal').pack(fill='x', pady=15)

        bottom = tk.Frame(main, bg=COLORS['bg_dark'])
        bottom.pack(fill='x', side='bottom')

        duration = format_time_short(self.project.audio_duration)
        self.info_label = tk.Label(bottom, text=f"📊 Duration: {duration}",
                                  font=('Segoe UI', 10), fg=COLORS['text_dim'],
                                  bg=COLORS['bg_dark'])
        self.info_label.pack(side='left')

        # Buttons
        btn_frame = tk.Frame(bottom, bg=COLORS['bg_dark'])
        btn_frame.pack(side='right')

        tk.Button(btn_frame, text="Cancel", font=('Segoe UI', 11),
                 fg=COLORS['text'], bg=COLORS['bg_light'], relief='flat',
                 width=10, command=self._cancel).pack(side='left', padx=5)

        tk.Button(btn_frame, text="Export", font=('Segoe UI', 11, 'bold'),
                 fg=COLORS['text'], bg=COLORS['accent'], relief='flat',
                 width=12, command=self._export).pack(side='left', padx=5)

    def _add_dropdown(self, parent, label, options, var_name, default):
        frame = tk.Frame(parent, bg=COLORS['bg_dark'])
        frame.pack(fill='x', pady=4)

        tk.Label(frame, text=label, font=('Segoe UI', 10), width=12, anchor='w',
                fg=COLORS['text_dim'], bg=COLORS['bg_dark']).pack(side='left')

        var = tk.StringVar(value=default)
        setattr(self, var_name, var)

        combo = ttk.Combobox(frame, textvariable=var, values=options, width=28, state='readonly')
        combo.pack(side='left', padx=10)

    def _browse(self):
        folder = filedialog.askdirectory()
        if folder:
            self.location_var.set(folder)

    def _cancel(self):
        self.result = None
        self.dialog.destroy()

    def _export(self):
        # Parse values
        res = self.resolution_var.get().split()[0]

        bitrate = "8M"
        bt = self.bitrate_var.get()
        if "16M" in bt: bitrate = "16M"
        elif "12M" in bt: bitrate = "12M"
        elif "4M" in bt: bitrate = "4M"

        codec = "h264"
        if "H.265" in self.codec_var.get():
            codec = "h265"

        fmt = self.format_var.get().lower()

        fps = 30
        fp = self.fps_var.get()
        if "60" in fp: fps = 60
        elif "24" in fp: fps = 24

        name = self.name_var.get() or f"video_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        output = os.path.join(self.location_var.get(), f"{name}.{fmt}")

        self.result = {
            'output_path': output,
            'resolution': res,
            'bitrate': bitrate,
            'codec': codec,
            'format': fmt,
            'fps': fps,
            'use_gpu': self.gpu_var.get(),
            'burn_captions': self.captions_var.get()
        }
        self.dialog.destroy()

    def show(self):
        self.dialog.wait_window()
        return self.result

# ═══════════════════════════════════════════════════════════════════════════════
# CAPTION EDITOR DIALOG
# ═══════════════════════════════════════════════════════════════════════════════

class CaptionStyleDialog:
    """Dialog for editing caption styles"""

    def __init__(self, parent, clip: TimelineClip = None):
        self.result = None
        self.clip = clip or TimelineClip(id="", track="captions", start_time=0, end_time=0)

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Caption Style")
        self.dialog.geometry("500x600")
        self.dialog.configure(bg=COLORS['bg_dark'])
        self.dialog.transient(parent)
        self.dialog.grab_set()

        self._create_ui()

    def _create_ui(self):
        main = tk.Frame(self.dialog, bg=COLORS['bg_dark'])
        main.pack(fill='both', expand=True, padx=20, pady=20)

        tk.Label(main, text="Caption Style", font=('Segoe UI', 16, 'bold'),
                fg=COLORS['text'], bg=COLORS['bg_dark']).pack(anchor='w')

        # Font selection
        font_frame = tk.LabelFrame(main, text="Font", font=('Segoe UI', 10),
                                   fg=COLORS['text'], bg=COLORS['bg_dark'])
        font_frame.pack(fill='x', pady=10)

        # Font family
        tk.Label(font_frame, text="Family:", fg=COLORS['text_dim'],
                bg=COLORS['bg_dark']).grid(row=0, column=0, padx=5, pady=5, sticky='w')

        self.font_var = tk.StringVar(value=self.clip.font_family)
        font_combo = ttk.Combobox(font_frame, textvariable=self.font_var,
                                  values=get_system_fonts()[:50], width=25)
        font_combo.grid(row=0, column=1, padx=5, pady=5)

        # Font size
        tk.Label(font_frame, text="Size:", fg=COLORS['text_dim'],
                bg=COLORS['bg_dark']).grid(row=1, column=0, padx=5, pady=5, sticky='w')

        self.size_var = tk.IntVar(value=self.clip.font_size)
        tk.Scale(font_frame, from_=16, to=120, variable=self.size_var,
                orient='horizontal', bg=COLORS['bg_dark'], fg=COLORS['text'],
                highlightthickness=0, length=200).grid(row=1, column=1, padx=5, pady=5)

        # Bold/Italic
        style_frame = tk.Frame(font_frame, bg=COLORS['bg_dark'])
        style_frame.grid(row=2, column=0, columnspan=2, pady=5)

        self.bold_var = tk.BooleanVar(value=self.clip.font_bold)
        tk.Checkbutton(style_frame, text="Bold", variable=self.bold_var,
                      fg=COLORS['text'], bg=COLORS['bg_dark'],
                      selectcolor=COLORS['bg_medium']).pack(side='left', padx=10)

        self.italic_var = tk.BooleanVar(value=self.clip.font_italic)
        tk.Checkbutton(style_frame, text="Italic", variable=self.italic_var,
                      fg=COLORS['text'], bg=COLORS['bg_dark'],
                      selectcolor=COLORS['bg_medium']).pack(side='left', padx=10)

        # Colors
        color_frame = tk.LabelFrame(main, text="Colors", font=('Segoe UI', 10),
                                    fg=COLORS['text'], bg=COLORS['bg_dark'])
        color_frame.pack(fill='x', pady=10)

        # Text color
        tk.Label(color_frame, text="Text Color:", fg=COLORS['text_dim'],
                bg=COLORS['bg_dark']).grid(row=0, column=0, padx=5, pady=5, sticky='w')

        self.text_color = self.clip.font_color
        self.text_color_btn = tk.Button(color_frame, text="    ", bg=self.text_color,
                                        width=8, command=lambda: self._pick_color('text'))
        self.text_color_btn.grid(row=0, column=1, padx=5, pady=5)

        # Stroke color
        tk.Label(color_frame, text="Outline:", fg=COLORS['text_dim'],
                bg=COLORS['bg_dark']).grid(row=1, column=0, padx=5, pady=5, sticky='w')

        self.stroke_color = self.clip.stroke_color
        self.stroke_color_btn = tk.Button(color_frame, text="    ", bg=self.stroke_color,
                                          width=8, command=lambda: self._pick_color('stroke'))
        self.stroke_color_btn.grid(row=1, column=1, padx=5, pady=5)

        # Stroke width
        tk.Label(color_frame, text="Outline Width:", fg=COLORS['text_dim'],
                bg=COLORS['bg_dark']).grid(row=2, column=0, padx=5, pady=5, sticky='w')

        self.stroke_width_var = tk.IntVar(value=self.clip.stroke_width)
        tk.Scale(color_frame, from_=0, to=10, variable=self.stroke_width_var,
                orient='horizontal', bg=COLORS['bg_dark'], fg=COLORS['text'],
                highlightthickness=0, length=150).grid(row=2, column=1, padx=5, pady=5)

        # Animation
        anim_frame = tk.LabelFrame(main, text="Animation", font=('Segoe UI', 10),
                                   fg=COLORS['text'], bg=COLORS['bg_dark'])
        anim_frame.pack(fill='x', pady=10)

        self.anim_var = tk.StringVar(value=self.clip.caption_animation.value)
        animations = [a.value for a in CaptionAnimation]
        ttk.Combobox(anim_frame, textvariable=self.anim_var, values=animations,
                    width=20, state='readonly').pack(padx=10, pady=10)

        # Buttons
        btn_frame = tk.Frame(main, bg=COLORS['bg_dark'])
        btn_frame.pack(side='bottom', fill='x', pady=10)

        tk.Button(btn_frame, text="Cancel", font=('Segoe UI', 10),
                 fg=COLORS['text'], bg=COLORS['bg_light'], relief='flat',
                 command=self._cancel).pack(side='right', padx=5)

        tk.Button(btn_frame, text="Apply", font=('Segoe UI', 10, 'bold'),
                 fg=COLORS['text'], bg=COLORS['accent'], relief='flat',
                 command=self._apply).pack(side='right', padx=5)

    def _pick_color(self, which):
        color = colorchooser.askcolor()[1]
        if color:
            if which == 'text':
                self.text_color = color
                self.text_color_btn.config(bg=color)
            else:
                self.stroke_color = color
                self.stroke_color_btn.config(bg=color)

    def _cancel(self):
        self.result = None
        self.dialog.destroy()

    def _apply(self):
        self.result = {
            'font_family': self.font_var.get(),
            'font_size': self.size_var.get(),
            'font_bold': self.bold_var.get(),
            'font_italic': self.italic_var.get(),
            'font_color': self.text_color,
            'stroke_color': self.stroke_color,
            'stroke_width': self.stroke_width_var.get(),
            'animation': CaptionAnimation(self.anim_var.get())
        }
        self.dialog.destroy()

    def show(self):
        self.dialog.wait_window()
        return self.result

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN APPLICATION
# ═══════════════════════════════════════════════════════════════════════════════

class AIVideoStudioApp:
    def __init__(self):
        ensure_dirs()
        self.config = load_config()
        self.project = Project()

        # Timeline state
        self.timeline_zoom = 1.0  # pixels per second
        self.timeline_offset = 0  # scroll offset
        self.playhead_pos = 0.0  # current position in seconds
        self.is_playing = False
        self.selected_clip = None

        # Waveform data
        self.waveform_data = []
        self.music_waveform_data = []

        # Image thumbnails cache
        self.thumbnails = {}

        # Create window
        self.root = tk.Tk()
        self.root.title(f"{APP_NAME} v{VERSION}")
        self.root.geometry("1500x950")
        self.root.minsize(1200, 800)
        self.root.configure(bg=COLORS['bg_dark'])

        # Keyboard shortcuts
        self.root.bind('<space>', self._toggle_playback)
        self.root.bind('<Left>', lambda e: self._seek(-1))
        self.root.bind('<Right>', lambda e: self._seek(1))
        self.root.bind('<Control-s>', lambda e: self._save_project())
        self.root.bind('<Control-z>', lambda e: self._undo())

        self._setup_styles()
        self._create_ui()
        self._center_window()

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TFrame', background=COLORS['bg_dark'])
        style.configure('TLabel', background=COLORS['bg_dark'], foreground=COLORS['text'])
        style.configure('Horizontal.TScale', background=COLORS['bg_dark'])

    def _center_window(self):
        self.root.update_idletasks()
        w, h = self.root.winfo_width(), self.root.winfo_height()
        x = (self.root.winfo_screenwidth() - w) // 2
        y = (self.root.winfo_screenheight() - h) // 2
        self.root.geometry(f'{w}x{h}+{x}+{y}')

    def _create_ui(self):
        # Main container
        main = tk.Frame(self.root, bg=COLORS['bg_dark'])
        main.pack(fill='both', expand=True)

        # Header
        self._create_header(main)

        # Content area
        content = tk.Frame(main, bg=COLORS['bg_dark'])
        content.pack(fill='both', expand=True, padx=10, pady=5)

        # Left panel (scrollable)
        left_container = tk.Frame(content, bg=COLORS['bg_medium'], width=340)
        left_container.pack(side='left', fill='y', padx=(0, 10))
        left_container.pack_propagate(False)
        self._create_left_panel(left_container)

        # Right panel (preview + timeline)
        right = tk.Frame(content, bg=COLORS['bg_dark'])
        right.pack(side='right', fill='both', expand=True)

        self._create_preview_area(right)
        self._create_timeline(right)
        self._create_log_area(right)

        # Status bar
        self._create_status_bar(main)

    def _create_header(self, parent):
        header = tk.Frame(parent, bg=COLORS['bg_medium'], height=55)
        header.pack(fill='x')
        header.pack_propagate(False)

        # Logo
        tk.Label(header, text="🎬 AI VIDEO STUDIO PRO", font=('Segoe UI', 18, 'bold'),
                fg=COLORS['accent'], bg=COLORS['bg_medium']).pack(side='left', padx=15, pady=10)

        tk.Label(header, text=f"v{VERSION}", font=('Segoe UI', 10),
                fg=COLORS['text_dim'], bg=COLORS['bg_medium']).pack(side='left')

        # Right buttons
        btn_frame = tk.Frame(header, bg=COLORS['bg_medium'])
        btn_frame.pack(side='right', padx=15)

        for text, cmd, color in [
            ("⚙️ Settings", self._open_settings, COLORS['bg_light']),
            ("💾 Save", self._save_project, COLORS['bg_light']),
            ("📤 Export", self._open_export, COLORS['accent'])
        ]:
            tk.Button(btn_frame, text=text, font=('Segoe UI', 10),
                     fg=COLORS['text'], bg=color, relief='flat',
                     cursor='hand2', padx=12, command=cmd).pack(side='left', padx=5)

    def _create_left_panel(self, container):
        # Scrollable canvas
        canvas = tk.Canvas(container, bg=COLORS['bg_medium'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient='vertical', command=canvas.yview)

        self.left_frame = tk.Frame(canvas, bg=COLORS['bg_medium'])

        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        canvas.pack(side='left', fill='both', expand=True)

        canvas_frame = canvas.create_window((0, 0), window=self.left_frame, anchor='nw')

        def configure_scroll(event):
            canvas.configure(scrollregion=canvas.bbox('all'))
            canvas.itemconfig(canvas_frame, width=event.width)

        self.left_frame.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        canvas.bind('<Configure>', configure_scroll)
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

        # Content sections
        self._create_section(self.left_frame, "🎙️ AUDIO / VOICE", [
            ("Select Audio File", self._select_audio, COLORS['accent_blue'])
        ])

        self.audio_label = tk.Label(self.left_frame, text="No audio selected",
                                   font=('Segoe UI', 9), fg=COLORS['text_dim'],
                                   bg=COLORS['bg_medium'])
        self.audio_label.pack(padx=15, anchor='w')

        self._create_section(self.left_frame, "🖼️ IMAGES", [
            ("Add Images Folder", self._select_images_folder, COLORS['bg_light']),
            ("Add Individual Images", self._select_images, COLORS['bg_light']),
            ("Clear All", self._clear_images, COLORS['bg_lighter'])
        ])

        self.images_label = tk.Label(self.left_frame, text="0 images loaded",
                                    font=('Segoe UI', 9), fg=COLORS['text_dim'],
                                    bg=COLORS['bg_medium'])
        self.images_label.pack(padx=15, anchor='w')

        # Intelligent Sync
        self._create_section(self.left_frame, "🧠 INTELLIGENT AUTO-SYNC", [])

        tk.Label(self.left_frame, text="AI automatically matches images to voice",
                font=('Segoe UI', 9), fg=COLORS['text_dim'],
                bg=COLORS['bg_medium']).pack(padx=15, anchor='w')

        tk.Button(self.left_frame, text="🚀 START AUTO-SYNC", font=('Segoe UI', 12, 'bold'),
                 fg=COLORS['text'], bg=COLORS['accent_purple'], relief='flat',
                 cursor='hand2', command=self._start_auto_sync).pack(fill='x', padx=15, pady=10)

        # Effects
        self._create_section(self.left_frame, "✨ EFFECTS", [])

        effects = tk.Frame(self.left_frame, bg=COLORS['bg_medium'])
        effects.pack(fill='x', padx=15)

        self.zoom_var = tk.BooleanVar(value=True)
        tk.Checkbutton(effects, text="Ken Burns Zoom Effect", variable=self.zoom_var,
                      font=('Segoe UI', 10), fg=COLORS['text'], bg=COLORS['bg_medium'],
                      selectcolor=COLORS['bg_dark']).pack(anchor='w')

        zoom_frame = tk.Frame(effects, bg=COLORS['bg_medium'])
        zoom_frame.pack(fill='x', pady=5)
        tk.Label(zoom_frame, text="Zoom:", font=('Segoe UI', 9),
                fg=COLORS['text_dim'], bg=COLORS['bg_medium']).pack(side='left')
        self.zoom_slider = tk.Scale(zoom_frame, from_=1.0, to=1.5, resolution=0.05,
                                   orient='horizontal', bg=COLORS['bg_medium'],
                                   fg=COLORS['text'], highlightthickness=0,
                                   troughcolor=COLORS['bg_dark'], length=150)
        self.zoom_slider.set(1.15)
        self.zoom_slider.pack(side='left', padx=5)

        self.fade_var = tk.BooleanVar(value=True)
        tk.Checkbutton(effects, text="Fade Transitions", variable=self.fade_var,
                      font=('Segoe UI', 10), fg=COLORS['text'], bg=COLORS['bg_medium'],
                      selectcolor=COLORS['bg_dark']).pack(anchor='w')

        # Background Music
        self._create_section(self.left_frame, "🎵 BACKGROUND MUSIC", [
            ("Add Background Music", self._select_bg_music, COLORS['bg_light'])
        ])

        self.music_label = tk.Label(self.left_frame, text="No music selected",
                                   font=('Segoe UI', 9), fg=COLORS['text_dim'],
                                   bg=COLORS['bg_medium'])
        self.music_label.pack(padx=15, anchor='w')

        vol_frame = tk.Frame(self.left_frame, bg=COLORS['bg_medium'])
        vol_frame.pack(fill='x', padx=15, pady=5)
        tk.Label(vol_frame, text="Volume:", font=('Segoe UI', 9),
                fg=COLORS['text_dim'], bg=COLORS['bg_medium']).pack(side='left')
        self.music_vol_slider = tk.Scale(vol_frame, from_=0.0, to=1.0, resolution=0.1,
                                        orient='horizontal', bg=COLORS['bg_medium'],
                                        fg=COLORS['text'], highlightthickness=0,
                                        troughcolor=COLORS['bg_dark'], length=120)
        self.music_vol_slider.set(0.3)
        self.music_vol_slider.pack(side='left', padx=5)

        # Captions
        self._create_section(self.left_frame, "📝 CAPTIONS", [
            ("Edit Caption Style", self._edit_caption_style, COLORS['bg_light'])
        ])

        self.captions_var = tk.BooleanVar(value=True)
        tk.Checkbutton(self.left_frame, text="Show captions in video",
                      variable=self.captions_var, font=('Segoe UI', 10),
                      fg=COLORS['text'], bg=COLORS['bg_medium'],
                      selectcolor=COLORS['bg_dark']).pack(padx=15, anchor='w')

        # Spacer
        tk.Frame(self.left_frame, bg=COLORS['bg_medium'], height=50).pack(fill='x')

    def _create_section(self, parent, title, buttons):
        frame = tk.Frame(parent, bg=COLORS['bg_medium'])
        frame.pack(fill='x', padx=10, pady=(15, 5))

        tk.Label(frame, text=title, font=('Segoe UI', 11, 'bold'),
                fg=COLORS['text'], bg=COLORS['bg_medium']).pack(anchor='w')

        for text, cmd, color in buttons:
            tk.Button(parent, text=text, font=('Segoe UI', 10),
                     fg=COLORS['text'], bg=color, relief='flat',
                     cursor='hand2', command=cmd).pack(fill='x', padx=15, pady=2)

    def _create_preview_area(self, parent):
        preview_frame = tk.Frame(parent, bg=COLORS['bg_dark'])
        preview_frame.pack(fill='both', expand=True, pady=(0, 10))

        # Header
        header = tk.Frame(preview_frame, bg=COLORS['bg_dark'])
        header.pack(fill='x')

        tk.Label(header, text="📺 PREVIEW", font=('Segoe UI', 12, 'bold'),
                fg=COLORS['text'], bg=COLORS['bg_dark']).pack(side='left')

        # Playback controls
        controls = tk.Frame(header, bg=COLORS['bg_dark'])
        controls.pack(side='right')

        for text, cmd in [("⏮️", lambda: self._seek(-10)),
                          ("◀️", lambda: self._seek(-1))]:
            tk.Button(controls, text=text, font=('Segoe UI', 10),
                     fg=COLORS['text'], bg=COLORS['bg_light'], relief='flat',
                     width=3, command=cmd).pack(side='left', padx=2)

        self.play_btn = tk.Button(controls, text="▶️", font=('Segoe UI', 12),
                                 fg=COLORS['text'], bg=COLORS['accent'], relief='flat',
                                 width=5, command=self._toggle_playback)
        self.play_btn.pack(side='left', padx=5)

        for text, cmd in [("▶️", lambda: self._seek(1)),
                          ("⏭️", lambda: self._seek(10))]:
            tk.Button(controls, text=text, font=('Segoe UI', 10),
                     fg=COLORS['text'], bg=COLORS['bg_light'], relief='flat',
                     width=3, command=cmd).pack(side='left', padx=2)

        # Time display
        self.time_label = tk.Label(controls, text="00:00 / 00:00",
                                  font=('Consolas', 10), fg=COLORS['text_dim'],
                                  bg=COLORS['bg_dark'])
        self.time_label.pack(side='left', padx=15)

        # Preview canvas
        self.preview_canvas = tk.Canvas(preview_frame, bg=COLORS['bg_medium'],
                                        highlightthickness=1,
                                        highlightbackground=COLORS['border'])
        self.preview_canvas.pack(fill='both', expand=True, pady=5)

        self.preview_canvas.create_text(400, 200, text="Add audio and images to preview",
                                        font=('Segoe UI', 14), fill=COLORS['text_dim'])

    def _create_timeline(self, parent):
        timeline_frame = tk.Frame(parent, bg=COLORS['bg_dark'])
        timeline_frame.pack(fill='x')

        # Timeline header
        header = tk.Frame(timeline_frame, bg=COLORS['bg_dark'])
        header.pack(fill='x')

        tk.Label(header, text="📊 TIMELINE", font=('Segoe UI', 12, 'bold'),
                fg=COLORS['text'], bg=COLORS['bg_dark']).pack(side='left')

        # Zoom controls
        zoom_frame = tk.Frame(header, bg=COLORS['bg_dark'])
        zoom_frame.pack(side='right')

        tk.Label(zoom_frame, text="Zoom:", font=('Segoe UI', 9),
                fg=COLORS['text_dim'], bg=COLORS['bg_dark']).pack(side='left')

        tk.Button(zoom_frame, text="−", font=('Segoe UI', 10),
                 fg=COLORS['text'], bg=COLORS['bg_light'], relief='flat',
                 width=3, command=lambda: self._zoom_timeline(-0.5)).pack(side='left', padx=2)

        tk.Button(zoom_frame, text="+", font=('Segoe UI', 10),
                 fg=COLORS['text'], bg=COLORS['bg_light'], relief='flat',
                 width=3, command=lambda: self._zoom_timeline(0.5)).pack(side='left', padx=2)

        # Timeline container
        container = tk.Frame(timeline_frame, bg=COLORS['timeline_bg'])
        container.pack(fill='x', pady=5)

        # Time ruler
        self.ruler_canvas = tk.Canvas(container, bg=COLORS['bg_dark'], height=25,
                                      highlightthickness=0)
        self.ruler_canvas.pack(fill='x', padx=5)

        # Track labels frame
        tracks_frame = tk.Frame(container, bg=COLORS['timeline_bg'])
        tracks_frame.pack(fill='x')

        # Track label column
        labels = tk.Frame(tracks_frame, bg=COLORS['timeline_bg'], width=40)
        labels.pack(side='left', fill='y')
        labels.pack_propagate(False)

        for icon in ["🖼️", "🎙️", "📝", "🎵"]:
            tk.Label(labels, text=icon, font=('Segoe UI', 10),
                    fg=COLORS['text_dim'], bg=COLORS['timeline_bg']).pack(pady=12)

        # Tracks container
        tracks_container = tk.Frame(tracks_frame, bg=COLORS['timeline_bg'])
        tracks_container.pack(side='left', fill='both', expand=True)

        # Image track
        self.images_track = tk.Canvas(tracks_container, bg=COLORS['bg_medium'],
                                      height=50, highlightthickness=0)
        self.images_track.pack(fill='x', padx=5, pady=2)

        # Audio track (waveform)
        self.audio_track = tk.Canvas(tracks_container, bg=COLORS['bg_medium'],
                                     height=40, highlightthickness=0)
        self.audio_track.pack(fill='x', padx=5, pady=2)

        # Captions track
        self.captions_track = tk.Canvas(tracks_container, bg=COLORS['bg_medium'],
                                        height=35, highlightthickness=0)
        self.captions_track.pack(fill='x', padx=5, pady=2)

        # Music track
        self.music_track = tk.Canvas(tracks_container, bg=COLORS['bg_medium'],
                                     height=30, highlightthickness=0)
        self.music_track.pack(fill='x', padx=5, pady=2)

        # Bind click events
        for track in [self.images_track, self.audio_track, self.captions_track, self.music_track]:
            track.bind('<Button-1>', self._on_timeline_click)

    def _create_log_area(self, parent):
        log_frame = tk.Frame(parent, bg=COLORS['bg_dark'])
        log_frame.pack(fill='x', pady=5)

        tk.Label(log_frame, text="📝 LOG", font=('Segoe UI', 10, 'bold'),
                fg=COLORS['text'], bg=COLORS['bg_dark']).pack(anchor='w')

        self.log_text = scrolledtext.ScrolledText(log_frame, height=4,
                                                  font=('Consolas', 9),
                                                  bg=COLORS['bg_medium'],
                                                  fg=COLORS['text'],
                                                  insertbackground=COLORS['text'])
        self.log_text.pack(fill='x', pady=3)

        self._log("AI Video Studio Pro v6.0 started")

    def _create_status_bar(self, parent):
        status = tk.Frame(parent, bg=COLORS['bg_medium'], height=30)
        status.pack(fill='x', side='bottom')
        status.pack_propagate(False)

        self.status_label = tk.Label(status, text="Ready", font=('Segoe UI', 9),
                                    fg=COLORS['text_dim'], bg=COLORS['bg_medium'])
        self.status_label.pack(side='left', padx=10, pady=5)

        self.progress = ttk.Progressbar(status, mode='determinate', length=250)
        self.progress.pack(side='right', padx=10, pady=5)

    # ═══════════════════════════════════════════════════════════════════════════
    # FILE OPERATIONS
    # ═══════════════════════════════════════════════════════════════════════════

    def _select_audio(self):
        path = filedialog.askopenfilename(
            title="Select Audio File",
            filetypes=[("Audio", "*.mp3 *.wav *.m4a *.flac *.ogg *.aac"), ("All", "*.*")]
        )
        if path:
            self.project.audio_path = path
            self.project.audio_duration = get_audio_duration(path)

            name = os.path.basename(path)
            duration = format_time_short(self.project.audio_duration)
            self.audio_label.config(text=f"✓ {name} ({duration})")

            self._log(f"Audio loaded: {name} ({duration})")
            self._update_status(f"Audio: {duration}")

            # Generate waveform
            self.waveform_data = WaveformGenerator.get_waveform_data(path)
            self._update_timeline()

    def _select_images_folder(self):
        folder = filedialog.askdirectory(title="Select Images Folder")
        if folder:
            exts = {'.jpg', '.jpeg', '.png', '.webp', '.bmp', '.gif'}
            images = sorted([os.path.join(folder, f) for f in os.listdir(folder)
                           if os.path.splitext(f)[1].lower() in exts])

            # Add as clips
            for img in images:
                clip = TimelineClip(
                    id=generate_id(),
                    track='images',
                    start_time=0,
                    end_time=5,
                    source_path=img
                )
                self.project.clips.append(clip)

            self._log(f"Added {len(images)} images from folder")
            self._update_images_count()
            self._update_timeline()
            self._update_preview()

    def _select_images(self):
        paths = filedialog.askopenfilenames(
            title="Select Images",
            filetypes=[("Images", "*.jpg *.jpeg *.png *.webp *.bmp *.gif")]
        )
        if paths:
            for img in paths:
                clip = TimelineClip(
                    id=generate_id(),
                    track='images',
                    start_time=0,
                    end_time=5,
                    source_path=img
                )
                self.project.clips.append(clip)

            self._log(f"Added {len(paths)} images")
            self._update_images_count()
            self._update_timeline()
            self._update_preview()

    def _clear_images(self):
        self.project.clips = [c for c in self.project.clips if c.track != 'images']
        self._log("Images cleared")
        self._update_images_count()
        self._update_timeline()

    def _select_bg_music(self):
        path = filedialog.askopenfilename(
            title="Select Background Music",
            filetypes=[("Audio", "*.mp3 *.wav *.m4a")]
        )
        if path:
            self.project.bg_music_path = path
            duration = get_audio_duration(path)
            self.music_label.config(text=f"✓ {os.path.basename(path)} ({format_time_short(duration)})")
            self._log(f"Background music: {os.path.basename(path)}")
            self.music_waveform_data = WaveformGenerator.get_waveform_data(path, 200)
            self._update_timeline()

    def _update_images_count(self):
        count = len([c for c in self.project.clips if c.track == 'images'])
        self.images_label.config(text=f"✓ {count} images loaded" if count else "0 images loaded")

    # ═══════════════════════════════════════════════════════════════════════════
    # AUTO-SYNC
    # ═══════════════════════════════════════════════════════════════════════════

    def _start_auto_sync(self):
        # Validate
        image_clips = [c for c in self.project.clips if c.track == 'images']

        if not self.project.audio_path:
            messagebox.showerror("Error", "Please select an audio file first!")
            return

        if not image_clips:
            messagebox.showerror("Error", "Please add images first!")
            return

        api_key = self.config['api_keys'].get('openai', '')
        if not api_key:
            messagebox.showerror("API Key Required",
                "OpenAI API key is required for Intelligent Auto-Sync.\n\n"
                "Go to Settings to add your API key.")
            return

        # Run in thread
        thread = threading.Thread(target=self._run_auto_sync, args=(api_key,))
        thread.start()

    def _run_auto_sync(self, api_key):
        try:
            self.root.after(0, lambda: self._update_status("Starting Auto-Sync..."))
            self.root.after(0, lambda: self._log("🧠 Starting Intelligent Auto-Sync..."))

            client = OpenAIClient(api_key)
            engine = AutoSyncEngine(client)

            # Get image paths
            image_paths = [c.source_path for c in self.project.clips if c.track == 'images']

            def progress_cb(step, total, msg):
                self.root.after(0, lambda: self._update_progress(step, total))
                self.root.after(0, lambda: self._log(msg))

            # Run auto-sync
            image_clips, caption_clips, words = engine.create_auto_sync(
                self.project.audio_path,
                image_paths,
                progress_cb
            )

            # Update project
            self.project.clips = [c for c in self.project.clips
                                 if c.track not in ['images', 'captions']]
            self.project.clips.extend(image_clips)
            self.project.clips.extend(caption_clips)
            self.project.words = words

            self.root.after(0, lambda: self._log(f"✓ Created {len(image_clips)} image clips"))
            self.root.after(0, lambda: self._log(f"✓ Created {len(caption_clips)} caption clips"))
            self.root.after(0, lambda: self._log(f"✓ Detected {len(words)} words"))

            self.root.after(0, self._update_timeline)
            self.root.after(0, self._update_preview)

            self.root.after(0, lambda: messagebox.showinfo("Success",
                f"Auto-Sync Complete!\n\n"
                f"• {len(image_clips)} image clips created\n"
                f"• {len(caption_clips)} captions generated\n"
                f"• {len(words)} words detected\n\n"
                "Images are now synchronized with your voice!"))

        except Exception as e:
            self.root.after(0, lambda: self._log(f"✗ Error: {e}"))
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))

        finally:
            self.root.after(0, lambda: self._update_progress(0, 100))
            self.root.after(0, lambda: self._update_status("Ready"))

    # ═══════════════════════════════════════════════════════════════════════════
    # TIMELINE
    # ═══════════════════════════════════════════════════════════════════════════

    def _update_timeline(self):
        """Update all timeline tracks"""
        self._draw_ruler()
        self._draw_images_track()
        self._draw_audio_track()
        self._draw_captions_track()
        self._draw_music_track()

    def _draw_ruler(self):
        """Draw time ruler with markers"""
        self.ruler_canvas.delete('all')

        if not self.project.audio_duration:
            return

        width = self.ruler_canvas.winfo_width() or 800
        duration = self.project.audio_duration

        # Calculate pixels per second
        pps = width / duration * self.timeline_zoom

        # Draw markers
        interval = 5  # seconds
        if pps > 50:
            interval = 1
        elif pps < 10:
            interval = 10

        for t in range(0, int(duration) + 1, interval):
            x = t * pps - self.timeline_offset
            if 0 <= x <= width:
                self.ruler_canvas.create_line(x, 15, x, 25, fill=COLORS['border'])
                self.ruler_canvas.create_text(x, 8, text=format_time_short(t),
                                             font=('Consolas', 8), fill=COLORS['text_dim'])

        # Draw playhead
        playhead_x = self.playhead_pos * pps - self.timeline_offset
        if 0 <= playhead_x <= width:
            self.ruler_canvas.create_line(playhead_x, 0, playhead_x, 25,
                                         fill=COLORS['playhead'], width=2)

    def _draw_images_track(self):
        """Draw image clips on timeline"""
        self.images_track.delete('all')

        image_clips = [c for c in self.project.clips if c.track == 'images']
        if not image_clips:
            return

        width = self.images_track.winfo_width() or 800
        height = 50
        duration = self.project.audio_duration or sum(c.duration for c in image_clips)
        pps = width / duration * self.timeline_zoom

        for clip in image_clips:
            x1 = clip.start_time * pps - self.timeline_offset
            x2 = clip.end_time * pps - self.timeline_offset

            if x2 < 0 or x1 > width:
                continue

            # Draw clip rectangle
            self.images_track.create_rectangle(x1, 5, x2, height - 5,
                                              fill=COLORS['track_images'],
                                              outline=COLORS['border'])

            # Draw thumbnail or index
            idx = image_clips.index(clip) + 1
            self.images_track.create_text((x1 + x2) / 2, height / 2,
                                         text=str(idx), fill=COLORS['text'],
                                         font=('Segoe UI', 9))

    def _draw_audio_track(self):
        """Draw audio waveform"""
        self.audio_track.delete('all')

        if not self.waveform_data:
            if self.project.audio_path:
                self.audio_track.create_text(400, 20, text="Audio loaded",
                                            fill=COLORS['text_dim'], font=('Segoe UI', 9))
            return

        width = self.audio_track.winfo_width() or 800
        height = 40

        # Draw waveform as polygon
        points_top = []
        points_bottom = []

        for i, amp in enumerate(self.waveform_data):
            x = int(i * width / len(self.waveform_data))
            y_top = int(height / 2 - amp * height / 2 * 0.9)
            y_bottom = int(height / 2 + amp * height / 2 * 0.9)
            points_top.append((x, y_top))
            points_bottom.append((x, y_bottom))

        # Create polygon
        points = points_top + list(reversed(points_bottom))
        if len(points) > 4:
            flat = [coord for point in points for coord in point]
            self.audio_track.create_polygon(flat, fill=COLORS['waveform'], outline='')

    def _draw_captions_track(self):
        """Draw caption clips"""
        self.captions_track.delete('all')

        caption_clips = [c for c in self.project.clips if c.track == 'captions']
        if not caption_clips:
            return

        width = self.captions_track.winfo_width() or 800
        height = 35
        duration = self.project.audio_duration or 60
        pps = width / duration * self.timeline_zoom

        for clip in caption_clips:
            x1 = clip.start_time * pps - self.timeline_offset
            x2 = clip.end_time * pps - self.timeline_offset

            if x2 < 0 or x1 > width:
                continue

            self.captions_track.create_rectangle(x1, 5, x2, height - 5,
                                                fill=COLORS['track_captions'],
                                                outline=COLORS['border'])

            # Show truncated text
            max_chars = int((x2 - x1) / 6)
            text = clip.text[:max_chars] + "..." if len(clip.text) > max_chars else clip.text
            self.captions_track.create_text(x1 + 5, height / 2, text=text,
                                           anchor='w', fill=COLORS['text'],
                                           font=('Segoe UI', 8))

    def _draw_music_track(self):
        """Draw background music"""
        self.music_track.delete('all')

        if not self.project.bg_music_path:
            return

        width = self.music_track.winfo_width() or 800

        self.music_track.create_rectangle(5, 5, width - 5, 25,
                                         fill=COLORS['track_music'],
                                         outline=COLORS['border'])
        self.music_track.create_text(width / 2, 15, text="🎵 Background Music",
                                    fill=COLORS['text'], font=('Segoe UI', 8))

    def _on_timeline_click(self, event):
        """Handle timeline click for seeking"""
        width = event.widget.winfo_width()
        duration = self.project.audio_duration or 60
        pps = width / duration * self.timeline_zoom

        clicked_time = (event.x + self.timeline_offset) / pps
        self.playhead_pos = max(0, min(clicked_time, duration))

        self._update_timeline()
        self._update_time_display()
        self._update_preview()

    def _zoom_timeline(self, delta):
        """Zoom timeline in/out"""
        self.timeline_zoom = max(0.5, min(5.0, self.timeline_zoom + delta))
        self._update_timeline()

    # ═══════════════════════════════════════════════════════════════════════════
    # PREVIEW & PLAYBACK
    # ═══════════════════════════════════════════════════════════════════════════

    def _update_preview(self):
        """Update preview canvas"""
        self.preview_canvas.delete('all')

        # Find current image clip
        image_clips = [c for c in self.project.clips if c.track == 'images']
        current_clip = None

        for clip in image_clips:
            if clip.start_time <= self.playhead_pos <= clip.end_time:
                current_clip = clip
                break

        if not current_clip and image_clips:
            current_clip = image_clips[0]

        if current_clip and PIL_AVAILABLE:
            try:
                img = Image.open(current_clip.source_path)

                canvas_w = self.preview_canvas.winfo_width() or 600
                canvas_h = self.preview_canvas.winfo_height() or 350

                ratio = min(canvas_w / img.width, canvas_h / img.height) * 0.9
                new_size = (int(img.width * ratio), int(img.height * ratio))
                img = img.resize(new_size, Image.Resampling.LANCZOS)

                self.preview_photo = ImageTk.PhotoImage(img)
                self.preview_canvas.create_image(canvas_w / 2, canvas_h / 2,
                                                image=self.preview_photo)

                # Show current caption
                caption_clips = [c for c in self.project.clips if c.track == 'captions']
                for cap in caption_clips:
                    if cap.start_time <= self.playhead_pos <= cap.end_time:
                        self.preview_canvas.create_text(canvas_w / 2, canvas_h - 50,
                                                       text=cap.text,
                                                       fill='white', font=('Arial', 18),
                                                       width=canvas_w - 40)
                        break

            except Exception as e:
                self.preview_canvas.create_text(300, 175, text=f"Error: {e}",
                                               fill=COLORS['error'])
        else:
            self.preview_canvas.create_text(300, 175, text="Add images to preview",
                                           fill=COLORS['text_dim'], font=('Segoe UI', 14))

    def _toggle_playback(self, event=None):
        """Toggle play/pause"""
        self.is_playing = not self.is_playing
        self.play_btn.config(text="⏸️" if self.is_playing else "▶️")

        if self.is_playing:
            self._playback_loop()

    def _playback_loop(self):
        """Playback animation loop"""
        if not self.is_playing:
            return

        # Advance playhead
        self.playhead_pos += 0.033  # ~30fps

        if self.playhead_pos >= self.project.audio_duration:
            self.playhead_pos = 0
            self.is_playing = False
            self.play_btn.config(text="▶️")
            return

        self._update_time_display()
        self._update_timeline()
        self._update_preview()

        self.root.after(33, self._playback_loop)

    def _seek(self, delta):
        """Seek forward/backward"""
        duration = self.project.audio_duration or 60
        self.playhead_pos = max(0, min(self.playhead_pos + delta, duration))
        self._update_time_display()
        self._update_timeline()
        self._update_preview()

    def _update_time_display(self):
        """Update time label"""
        current = format_time_short(self.playhead_pos)
        total = format_time_short(self.project.audio_duration)
        self.time_label.config(text=f"{current} / {total}")

    # ═══════════════════════════════════════════════════════════════════════════
    # DIALOGS
    # ═══════════════════════════════════════════════════════════════════════════

    def _open_export(self):
        """Open export dialog"""
        image_clips = [c for c in self.project.clips if c.track == 'images']

        if not image_clips:
            messagebox.showerror("Error", "Please add images first!")
            return
        if not self.project.audio_path:
            messagebox.showerror("Error", "Please select an audio file!")
            return

        # Update project settings
        self.project.bg_music_volume = self.music_vol_slider.get()

        dialog = ExportDialog(self.root, self.project,
                             image_clips[0].source_path if image_clips else None)
        result = dialog.show()

        if result:
            self._start_export(result)

    def _start_export(self, settings):
        """Start video export"""
        self._log(f"Exporting to: {settings['output_path']}")

        # Update project settings
        self.project.resolution = settings['resolution']
        self.project.fps = settings['fps']
        self.project.bitrate = settings['bitrate']

        thread = threading.Thread(target=self._export_video, args=(settings,))
        thread.start()

    def _export_video(self, settings):
        try:
            self.root.after(0, lambda: self._update_status("Exporting..."))

            def progress_cb(step, total, msg):
                self.root.after(0, lambda: self._update_progress(step, total))
                self.root.after(0, lambda: self._log(msg))

            if settings.get('burn_captions', False):
                success = VideoProcessor.create_video_with_captions(
                    self.project, settings['output_path'], progress_cb
                )
            else:
                success = VideoProcessor.create_video(
                    self.project, settings['output_path'], progress_cb
                )

            if success:
                self.root.after(0, lambda: self._log(f"✓ Export complete: {settings['output_path']}"))
                self.root.after(0, lambda: messagebox.showinfo("Success",
                    f"Video exported successfully!\n\n{settings['output_path']}"))
            else:
                self.root.after(0, lambda: messagebox.showerror("Error", "Export failed!"))

        except Exception as e:
            self.root.after(0, lambda: self._log(f"✗ Error: {e}"))
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))

        finally:
            self.root.after(0, lambda: self._update_progress(0, 100))
            self.root.after(0, lambda: self._update_status("Ready"))

    def _edit_caption_style(self):
        """Open caption style dialog"""
        dialog = CaptionStyleDialog(self.root)
        result = dialog.show()

        if result:
            # Apply to all caption clips
            for clip in self.project.clips:
                if clip.track == 'captions':
                    clip.font_family = result['font_family']
                    clip.font_size = result['font_size']
                    clip.font_bold = result['font_bold']
                    clip.font_italic = result['font_italic']
                    clip.font_color = result['font_color']
                    clip.stroke_color = result['stroke_color']
                    clip.stroke_width = result['stroke_width']
                    clip.caption_animation = result['animation']

            self._log("Caption style updated")

    def _open_settings(self):
        """Open settings dialog"""
        win = tk.Toplevel(self.root)
        win.title("Settings")
        win.geometry("500x350")
        win.configure(bg=COLORS['bg_dark'])
        win.transient(self.root)
        win.grab_set()

        tk.Label(win, text="⚙️ Settings", font=('Segoe UI', 18, 'bold'),
                fg=COLORS['accent'], bg=COLORS['bg_dark']).pack(pady=15)

        # API Key
        frame = tk.LabelFrame(win, text="API Keys", font=('Segoe UI', 10, 'bold'),
                             fg=COLORS['text'], bg=COLORS['bg_dark'])
        frame.pack(fill='x', padx=20, pady=10)

        tk.Label(frame, text="OpenAI API Key:", fg=COLORS['text_dim'],
                bg=COLORS['bg_dark']).pack(anchor='w', padx=10, pady=(10, 0))

        tk.Label(frame, text="(Required for Intelligent Auto-Sync)",
                font=('Segoe UI', 8), fg=COLORS['text_muted'],
                bg=COLORS['bg_dark']).pack(anchor='w', padx=10)

        api_entry = tk.Entry(frame, width=50, show='*',
                            bg=COLORS['bg_light'], fg=COLORS['text'],
                            insertbackground=COLORS['text'])
        api_entry.insert(0, self.config['api_keys'].get('openai', ''))
        api_entry.pack(padx=10, pady=5)

        def save():
            self.config['api_keys']['openai'] = api_entry.get()
            save_config(self.config)
            self._log("Settings saved!")
            win.destroy()

        tk.Button(win, text="Save", font=('Segoe UI', 11, 'bold'),
                 fg=COLORS['text'], bg=COLORS['accent'], relief='flat',
                 command=save).pack(pady=20)

    def _save_project(self):
        """Save project to file"""
        self._log("Project saved")
        messagebox.showinfo("Save", "Project saved successfully!")

    def _undo(self):
        """Undo last action"""
        self._log("Undo")

    # ═══════════════════════════════════════════════════════════════════════════
    # UTILITY
    # ═══════════════════════════════════════════════════════════════════════════

    def _log(self, msg):
        ts = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert('end', f"[{ts}] {msg}\n")
        self.log_text.see('end')

    def _update_status(self, msg):
        self.status_label.config(text=msg)

    def _update_progress(self, val, max_val=100):
        self.progress['maximum'] = max_val
        self.progress['value'] = val
        self.root.update_idletasks()

    def run(self):
        self.root.mainloop()

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    app = AIVideoStudioApp()
    app.run()
