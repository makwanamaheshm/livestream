#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════╗
║                    AI VIDEO STUDIO PRO v5.0                          ║
║           Professional Video Editor - CapCut Style                   ║
╠══════════════════════════════════════════════════════════════════════╣
║  Features:                                                            ║
║  ✓ Professional Export Dialog (Resolution, Codec, Bitrate, FPS)      ║
║  ✓ Timeline with Audio Waveform                                      ║
║  ✓ Video Preview & Playback                                          ║
║  ✓ Ken Burns Effect (Slow Zoom)                                      ║
║  ✓ Fade/Crossfade Transitions                                        ║
║  ✓ Background Music Support                                          ║
║  ✓ Overlay/Watermark Support                                         ║
║  ✓ Intelligent Voice-Image Sync                                      ║
║  ✓ GPU Acceleration (NVENC/QSV)                                      ║
╚══════════════════════════════════════════════════════════════════════╝
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
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from tkinter import font as tkfont

# PIL for images
try:
    from PIL import Image, ImageTk, ImageDraw, ImageFilter
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# ═══════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════

APP_NAME = "AI Video Studio Pro"
VERSION = "5.0.0"
APP_DIR = Path(__file__).parent
CONFIG_FILE = APP_DIR / "config.json"
PROJECTS_DIR = APP_DIR / "projects"
TEMP_DIR = APP_DIR / "temp"

# Modern Dark Theme Colors
COLORS = {
    'bg_dark': '#0d1117',
    'bg_medium': '#161b22',
    'bg_light': '#21262d',
    'bg_lighter': '#30363d',
    'accent': '#238636',
    'accent_blue': '#1f6feb',
    'accent_red': '#f85149',
    'accent_orange': '#d29922',
    'text': '#f0f6fc',
    'text_dim': '#8b949e',
    'text_muted': '#6e7681',
    'border': '#30363d',
    'success': '#3fb950',
    'warning': '#d29922',
    'error': '#f85149',
    'timeline_bg': '#0d1117',
    'waveform': '#58a6ff'
}

DEFAULT_CONFIG = {
    "api_keys": {"openai": "", "elevenlabs": "", "ideogram": ""},
    "export": {
        "resolution": "1920x1080",
        "bitrate": "8M",
        "codec": "h264",
        "format": "mp4",
        "fps": 30,
        "use_gpu": True
    },
    "settings": {
        "transition_duration": 1.0,
        "zoom_intensity": 1.2,
        "default_image_duration": 5.0
    }
}

# ═══════════════════════════════════════════════════════════════════
# UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════

def ensure_dirs():
    PROJECTS_DIR.mkdir(parents=True, exist_ok=True)
    TEMP_DIR.mkdir(parents=True, exist_ok=True)

def load_config():
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r') as f:
                cfg = json.load(f)
                # Merge with defaults
                for key in DEFAULT_CONFIG:
                    if key not in cfg:
                        cfg[key] = DEFAULT_CONFIG[key]
                return cfg
        except:
            pass
    return DEFAULT_CONFIG.copy()

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
    mins = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{mins:02d}:{secs:02d}"

def format_duration(seconds):
    hours = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    if hours > 0:
        return f"{hours}h {mins}m {secs}s"
    return f"{mins}m {secs}s"

def get_file_size_estimate(duration, bitrate_str):
    """Estimate file size based on duration and bitrate"""
    bitrate = int(bitrate_str.replace('M', '000000').replace('K', '000'))
    size_bytes = (bitrate * duration) / 8
    size_mb = size_bytes / (1024 * 1024)
    if size_mb >= 1024:
        return f"{size_mb/1024:.2f} GB"
    return f"{size_mb:.2f} MB"

def check_gpu_available():
    """Check if GPU encoding is available"""
    # Check NVIDIA NVENC
    try:
        result = subprocess.run(['ffmpeg', '-hide_banner', '-encoders'],
                               capture_output=True, text=True)
        if 'h264_nvenc' in result.stdout:
            return 'nvenc'
        if 'h264_qsv' in result.stdout:
            return 'qsv'
        if 'h264_amf' in result.stdout:
            return 'amf'
    except:
        pass
    return None

def get_audio_waveform_data(audio_path, num_samples=200):
    """Extract waveform data from audio file"""
    try:
        # Convert to wav first
        temp_wav = TEMP_DIR / "temp_waveform.wav"
        subprocess.run([
            'ffmpeg', '-y', '-i', audio_path,
            '-ac', '1', '-ar', '8000',
            str(temp_wav)
        ], capture_output=True)

        if not temp_wav.exists():
            return None

        with wave.open(str(temp_wav), 'rb') as wav:
            n_frames = wav.getnframes()
            frames = wav.readframes(n_frames)
            samples = struct.unpack(f'{n_frames}h', frames)

            # Downsample to num_samples
            chunk_size = len(samples) // num_samples
            waveform = []
            for i in range(num_samples):
                chunk = samples[i * chunk_size:(i + 1) * chunk_size]
                if chunk:
                    avg = sum(abs(s) for s in chunk) / len(chunk)
                    waveform.append(avg / 32768.0)  # Normalize

            temp_wav.unlink()
            return waveform
    except Exception as e:
        print(f"Waveform error: {e}")
    return None

# ═══════════════════════════════════════════════════════════════════
# VIDEO PROCESSOR
# ═══════════════════════════════════════════════════════════════════

class VideoProcessor:
    """Professional video processing with effects"""

    @staticmethod
    def create_video(images, durations, audio_path, output_path,
                    resolution="1920x1080", bitrate="8M", codec="h264",
                    fps=30, use_gpu=True, zoom_enabled=True, zoom_intensity=1.2,
                    fade_enabled=True, fade_duration=1.0,
                    bg_music_path=None, bg_music_volume=0.3,
                    overlay_path=None,
                    progress_callback=None):
        """Create video with all effects"""

        if not images or not durations:
            return False

        width, height = map(int, resolution.split('x'))
        temp_dir = Path(output_path).parent / f"temp_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        temp_dir.mkdir(exist_ok=True)

        try:
            total_steps = len(images) + 2
            current_step = 0

            # Determine encoder
            encoder = 'libx264'
            encoder_opts = ['-preset', 'medium']

            if use_gpu:
                gpu_type = check_gpu_available()
                if gpu_type == 'nvenc':
                    encoder = 'h264_nvenc'
                    encoder_opts = ['-preset', 'p4', '-tune', 'hq']
                elif gpu_type == 'qsv':
                    encoder = 'h264_qsv'
                    encoder_opts = ['-preset', 'medium']
                elif gpu_type == 'amf':
                    encoder = 'h264_amf'
                    encoder_opts = []

            # Process each image with Ken Burns
            clips = []
            for i, (img, dur) in enumerate(zip(images, durations)):
                if progress_callback:
                    progress_callback(i, total_steps, f"Processing image {i+1}/{len(images)}")

                clip_path = temp_dir / f"clip_{i:04d}.mp4"

                if zoom_enabled:
                    # Ken Burns with random direction
                    import random
                    if random.choice([True, False]):
                        start_s, end_s = 1.0, zoom_intensity
                    else:
                        start_s, end_s = zoom_intensity, 1.0

                    frames = int(dur * fps)
                    zoom_filter = (
                        f"zoompan=z='if(eq(on,1),{start_s},{start_s}+({end_s}-{start_s})*on/{frames})':"
                        f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
                        f"d={frames}:s={width}x{height}:fps={fps}"
                    )

                    cmd = [
                        'ffmpeg', '-y', '-loop', '1', '-i', img,
                        '-vf', zoom_filter,
                        '-c:v', encoder, *encoder_opts,
                        '-t', str(dur), '-pix_fmt', 'yuv420p',
                        '-an', str(clip_path)
                    ]
                else:
                    # Simple scale
                    cmd = [
                        'ffmpeg', '-y', '-loop', '1', '-i', img,
                        '-vf', f'scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2',
                        '-c:v', encoder, *encoder_opts,
                        '-t', str(dur), '-pix_fmt', 'yuv420p',
                        '-an', str(clip_path)
                    ]

                subprocess.run(cmd, capture_output=True)
                clips.append(str(clip_path))

            current_step = len(images)
            if progress_callback:
                progress_callback(current_step, total_steps, "Adding transitions...")

            # Apply fade transitions
            if fade_enabled and len(clips) > 1:
                faded_clips = []
                for i, clip in enumerate(clips):
                    faded = temp_dir / f"faded_{i:04d}.mp4"
                    filters = []

                    dur = durations[i]
                    if i > 0:
                        filters.append(f"fade=t=in:st=0:d={fade_duration}")
                    if i < len(clips) - 1:
                        filters.append(f"fade=t=out:st={dur-fade_duration}:d={fade_duration}")

                    if filters:
                        cmd = ['ffmpeg', '-y', '-i', clip, '-vf', ','.join(filters),
                               '-c:v', encoder, *encoder_opts, '-an', str(faded)]
                        subprocess.run(cmd, capture_output=True)
                        faded_clips.append(str(faded))
                    else:
                        faded_clips.append(clip)

                clips = faded_clips

            current_step += 1
            if progress_callback:
                progress_callback(current_step, total_steps, "Combining video and audio...")

            # Concatenate clips
            concat_file = temp_dir / "concat.txt"
            with open(concat_file, 'w') as f:
                for clip in clips:
                    f.write(f"file '{clip}'\n")

            temp_video = temp_dir / "temp_video.mp4"

            # Build final command
            cmd = [
                'ffmpeg', '-y',
                '-f', 'concat', '-safe', '0', '-i', str(concat_file),
                '-i', audio_path
            ]

            # Add background music if specified
            filter_complex = []
            if bg_music_path and os.path.exists(bg_music_path):
                cmd.extend(['-i', bg_music_path])
                # Mix audio: narration at full volume, music at bg_music_volume
                filter_complex.append(
                    f"[1:a]volume=1.0[narration];"
                    f"[2:a]volume={bg_music_volume}[music];"
                    f"[narration][music]amix=inputs=2:duration=first[aout]"
                )

            # Video filter for overlay
            if overlay_path and os.path.exists(overlay_path):
                cmd.extend(['-i', overlay_path])
                overlay_idx = 3 if bg_music_path else 2
                filter_complex.append(
                    f"[{overlay_idx}:v]scale=150:-1,format=rgba,colorchannelmixer=aa=0.7[ovr];"
                    f"[0:v][ovr]overlay=W-w-20:H-h-20[vout]"
                )

            if filter_complex:
                cmd.extend(['-filter_complex', ';'.join(filter_complex)])
                if bg_music_path:
                    cmd.extend(['-map', '[vout]' if overlay_path else '0:v', '-map', '[aout]'])
                else:
                    cmd.extend(['-map', '[vout]' if overlay_path else '0:v', '-map', '1:a'])

            cmd.extend([
                '-c:v', encoder, *encoder_opts,
                '-b:v', bitrate,
                '-r', str(fps),
                '-c:a', 'aac', '-b:a', '192k',
                '-shortest',
                '-movflags', '+faststart',
                output_path
            ])

            subprocess.run(cmd, capture_output=True)

            # Cleanup
            shutil.rmtree(temp_dir, ignore_errors=True)

            return os.path.exists(output_path)

        except Exception as e:
            print(f"Error: {e}")
            shutil.rmtree(temp_dir, ignore_errors=True)
            return False

# ═══════════════════════════════════════════════════════════════════
# OPENAI CLIENT FOR INTELLIGENT SYNC
# ═══════════════════════════════════════════════════════════════════

class OpenAIClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    def transcribe(self, audio_path, progress_callback=None):
        """Transcribe audio with word timestamps"""
        if progress_callback:
            progress_callback("Transcribing audio...")

        try:
            with open(audio_path, 'rb') as f:
                response = requests.post(
                    "https://api.openai.com/v1/audio/transcriptions",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    files={"file": f},
                    data={
                        "model": "whisper-1",
                        "response_format": "verbose_json",
                        "timestamp_granularities[]": "word"
                    },
                    timeout=600
                )

            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Transcription error: {e}")
        return None

    def analyze_image(self, image_path):
        """Analyze image content"""
        try:
            with open(image_path, "rb") as f:
                img_data = base64.b64encode(f.read()).decode('utf-8')

            ext = os.path.splitext(image_path)[1].lower()
            media = {'.jpg': 'image/jpeg', '.jpeg': 'image/jpeg',
                    '.png': 'image/png', '.webp': 'image/webp'}.get(ext, 'image/jpeg')

            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=self.headers,
                json={
                    "model": "gpt-4o-mini",
                    "messages": [{
                        "role": "user",
                        "content": [
                            {"type": "image_url", "image_url": {"url": f"data:{media};base64,{img_data}", "detail": "low"}},
                            {"type": "text", "text": "Describe this image in 10 keywords. Return only comma-separated keywords."}
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

    def match_images(self, segments, images_info):
        """Match images to transcript segments using AI"""
        try:
            prompt = f"""Match these transcript segments to the most relevant images.

SEGMENTS:
{json.dumps([{'id': i, 'text': s['text'][:100]} for i, s in enumerate(segments)], indent=2)}

IMAGES:
{json.dumps([{'id': i, 'keywords': info} for i, info in enumerate(images_info)], indent=2)}

Return JSON array: [{{"segment_id": 0, "image_id": 2}}, ...]
Match EVERY segment to an image. Same image can be used multiple times."""

            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=self.headers,
                json={
                    "model": "gpt-4o-mini",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 1500
                },
                timeout=60
            )

            if response.status_code == 200:
                content = response.json()['choices'][0]['message']['content']
                match = re.search(r'\[.*\]', content, re.DOTALL)
                if match:
                    return json.loads(match.group())
        except Exception as e:
            print(f"Matching error: {e}")
        return None


# ═══════════════════════════════════════════════════════════════════
# EXPORT DIALOG
# ═══════════════════════════════════════════════════════════════════

class ExportDialog:
    """CapCut-style export dialog"""

    def __init__(self, parent, config, audio_duration, first_image=None):
        self.result = None
        self.config = config
        self.audio_duration = audio_duration

        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Export Video")
        self.dialog.geometry("600x700")
        self.dialog.configure(bg=COLORS['bg_dark'])
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.resizable(False, False)

        # Center dialog
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - 600) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 700) // 2
        self.dialog.geometry(f"+{x}+{y}")

        self.create_ui(first_image)

    def create_ui(self, first_image):
        # Main container
        main = tk.Frame(self.dialog, bg=COLORS['bg_dark'])
        main.pack(fill='both', expand=True, padx=20, pady=20)

        # Title
        tk.Label(main, text="Export Video", font=('Segoe UI', 18, 'bold'),
                fg=COLORS['text'], bg=COLORS['bg_dark']).pack(anchor='w')

        # Preview thumbnail
        preview_frame = tk.Frame(main, bg=COLORS['bg_medium'], height=150)
        preview_frame.pack(fill='x', pady=15)
        preview_frame.pack_propagate(False)

        if first_image and PIL_AVAILABLE:
            try:
                img = Image.open(first_image)
                img.thumbnail((200, 130))
                self.preview_img = ImageTk.PhotoImage(img)
                tk.Label(preview_frame, image=self.preview_img, bg=COLORS['bg_medium']).pack(side='left', padx=10, pady=10)
            except:
                pass

        # File info on right of preview
        info_frame = tk.Frame(preview_frame, bg=COLORS['bg_medium'])
        info_frame.pack(side='left', fill='both', expand=True, padx=10, pady=10)

        # Name field
        tk.Label(info_frame, text="Name", font=('Segoe UI', 9),
                fg=COLORS['text_dim'], bg=COLORS['bg_medium']).pack(anchor='w')
        self.name_var = tk.StringVar(value=f"video_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        name_entry = tk.Entry(info_frame, textvariable=self.name_var, font=('Segoe UI', 11),
                             bg=COLORS['bg_light'], fg=COLORS['text'], insertbackground=COLORS['text'],
                             relief='flat', width=30)
        name_entry.pack(anchor='w', pady=(2, 10))

        # Export location
        tk.Label(info_frame, text="Export to", font=('Segoe UI', 9),
                fg=COLORS['text_dim'], bg=COLORS['bg_medium']).pack(anchor='w')

        loc_frame = tk.Frame(info_frame, bg=COLORS['bg_medium'])
        loc_frame.pack(anchor='w', fill='x')

        self.location_var = tk.StringVar(value=str(PROJECTS_DIR))
        loc_entry = tk.Entry(loc_frame, textvariable=self.location_var, font=('Segoe UI', 10),
                            bg=COLORS['bg_light'], fg=COLORS['text'], insertbackground=COLORS['text'],
                            relief='flat', width=25)
        loc_entry.pack(side='left')

        browse_btn = tk.Button(loc_frame, text="📁", font=('Segoe UI', 10),
                              bg=COLORS['bg_light'], fg=COLORS['text'], relief='flat',
                              command=self.browse_location)
        browse_btn.pack(side='left', padx=5)

        # Separator
        ttk.Separator(main, orient='horizontal').pack(fill='x', pady=15)

        # Video settings section
        video_header = tk.Frame(main, bg=COLORS['bg_dark'])
        video_header.pack(fill='x')

        self.video_enabled = tk.BooleanVar(value=True)
        video_cb = tk.Checkbutton(video_header, text="Video", variable=self.video_enabled,
                                  font=('Segoe UI', 12, 'bold'), fg=COLORS['text'],
                                  bg=COLORS['bg_dark'], selectcolor=COLORS['bg_medium'],
                                  activebackground=COLORS['bg_dark'])
        video_cb.pack(side='left')

        video_settings = tk.Frame(main, bg=COLORS['bg_dark'])
        video_settings.pack(fill='x', pady=10)

        # Resolution
        self.create_dropdown(video_settings, "Resolution",
                            ["3840x2160 (4K)", "1920x1080 (Full HD)", "1280x720 (HD)", "854x480 (SD)"],
                            "resolution_var", "1920x1080 (Full HD)")

        # Bitrate
        self.create_dropdown(video_settings, "Bit rate",
                            ["Higher (12M)", "Recommended (8M)", "Lower (4M)", "Custom"],
                            "bitrate_var", "Recommended (8M)")

        # Codec
        self.create_dropdown(video_settings, "Codec",
                            ["H.264 (Recommended)", "H.265/HEVC", "VP9"],
                            "codec_var", "H.264 (Recommended)")

        # Format
        self.create_dropdown(video_settings, "Format",
                            ["MP4", "MOV", "MKV", "AVI"],
                            "format_var", "MP4")

        # Frame rate
        self.create_dropdown(video_settings, "Frame rate",
                            ["60 fps", "30 fps", "24 fps"],
                            "fps_var", "30 fps")

        # GPU acceleration
        gpu_frame = tk.Frame(video_settings, bg=COLORS['bg_dark'])
        gpu_frame.pack(fill='x', pady=5)

        self.gpu_var = tk.BooleanVar(value=True)
        gpu_cb = tk.Checkbutton(gpu_frame, text="Use GPU Acceleration (Faster Export)",
                               variable=self.gpu_var, font=('Segoe UI', 10),
                               fg=COLORS['text'], bg=COLORS['bg_dark'],
                               selectcolor=COLORS['bg_medium'])
        gpu_cb.pack(side='left')

        gpu_status = check_gpu_available()
        if gpu_status:
            tk.Label(gpu_frame, text=f"✓ {gpu_status.upper()} detected",
                    font=('Segoe UI', 9), fg=COLORS['success'], bg=COLORS['bg_dark']).pack(side='left', padx=10)
        else:
            tk.Label(gpu_frame, text="No GPU encoder found",
                    font=('Segoe UI', 9), fg=COLORS['text_dim'], bg=COLORS['bg_dark']).pack(side='left', padx=10)
            self.gpu_var.set(False)

        # Separator
        ttk.Separator(main, orient='horizontal').pack(fill='x', pady=15)

        # File info at bottom
        info_bottom = tk.Frame(main, bg=COLORS['bg_dark'])
        info_bottom.pack(fill='x', side='bottom', pady=10)

        # Duration and size estimate
        duration_text = format_duration(self.audio_duration)
        size_estimate = get_file_size_estimate(self.audio_duration, "8M")

        self.info_label = tk.Label(info_bottom,
                                   text=f"📊 Duration: {duration_text}  |  Size: about {size_estimate}",
                                   font=('Segoe UI', 10), fg=COLORS['text_dim'], bg=COLORS['bg_dark'])
        self.info_label.pack(side='left')

        # Buttons
        btn_frame = tk.Frame(info_bottom, bg=COLORS['bg_dark'])
        btn_frame.pack(side='right')

        cancel_btn = tk.Button(btn_frame, text="Cancel", font=('Segoe UI', 11),
                              fg=COLORS['text'], bg=COLORS['bg_light'], relief='flat',
                              width=10, cursor='hand2', command=self.cancel)
        cancel_btn.pack(side='left', padx=5)

        export_btn = tk.Button(btn_frame, text="Export", font=('Segoe UI', 11, 'bold'),
                              fg=COLORS['text'], bg=COLORS['accent'], relief='flat',
                              width=10, cursor='hand2', command=self.export)
        export_btn.pack(side='left', padx=5)

    def create_dropdown(self, parent, label, options, var_name, default):
        frame = tk.Frame(parent, bg=COLORS['bg_dark'])
        frame.pack(fill='x', pady=3)

        tk.Label(frame, text=label, font=('Segoe UI', 10), width=12, anchor='w',
                fg=COLORS['text_dim'], bg=COLORS['bg_dark']).pack(side='left')

        var = tk.StringVar(value=default)
        setattr(self, var_name, var)

        combo = ttk.Combobox(frame, textvariable=var, values=options, width=25, state='readonly')
        combo.pack(side='left', padx=10)

        # Update size estimate when bitrate changes
        if var_name == 'bitrate_var':
            combo.bind('<<ComboboxSelected>>', self.update_size_estimate)

    def update_size_estimate(self, event=None):
        bitrate_text = self.bitrate_var.get()
        bitrate = "8M"
        if "12M" in bitrate_text:
            bitrate = "12M"
        elif "4M" in bitrate_text:
            bitrate = "4M"

        size = get_file_size_estimate(self.audio_duration, bitrate)
        duration = format_duration(self.audio_duration)
        self.info_label.config(text=f"📊 Duration: {duration}  |  Size: about {size}")

    def browse_location(self):
        folder = filedialog.askdirectory()
        if folder:
            self.location_var.set(folder)

    def cancel(self):
        self.result = None
        self.dialog.destroy()

    def export(self):
        # Parse values
        res = self.resolution_var.get().split()[0]

        bitrate = "8M"
        bt = self.bitrate_var.get()
        if "12M" in bt:
            bitrate = "12M"
        elif "4M" in bt:
            bitrate = "4M"

        codec = "h264"
        cd = self.codec_var.get()
        if "H.265" in cd:
            codec = "h265"
        elif "VP9" in cd:
            codec = "vp9"

        fmt = self.format_var.get().lower()

        fps = 30
        fp = self.fps_var.get()
        if "60" in fp:
            fps = 60
        elif "24" in fp:
            fps = 24

        # Build output path
        name = self.name_var.get() or f"video_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        output_path = os.path.join(self.location_var.get(), f"{name}.{fmt}")

        self.result = {
            'output_path': output_path,
            'resolution': res,
            'bitrate': bitrate,
            'codec': codec,
            'format': fmt,
            'fps': fps,
            'use_gpu': self.gpu_var.get()
        }

        self.dialog.destroy()

    def show(self):
        self.dialog.wait_window()
        return self.result


# ═══════════════════════════════════════════════════════════════════
# MAIN APPLICATION
# ═══════════════════════════════════════════════════════════════════

class AIVideoStudioApp:
    def __init__(self):
        ensure_dirs()
        self.config = load_config()

        # Project data
        self.images = []
        self.audio_path = None
        self.audio_duration = 0
        self.overlay_path = None
        self.bg_music_path = None
        self.waveform_data = None
        self.image_thumbnails = []

        # Create window
        self.root = tk.Tk()
        self.root.title(f"{APP_NAME} v{VERSION}")
        self.root.geometry("1400x900")
        self.root.minsize(1200, 800)
        self.root.configure(bg=COLORS['bg_dark'])

        # Style
        self.setup_styles()

        # Create UI
        self.create_ui()

        self.center_window()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TFrame', background=COLORS['bg_dark'])
        style.configure('TLabel', background=COLORS['bg_dark'], foreground=COLORS['text'])
        style.configure('TCheckbutton', background=COLORS['bg_dark'], foreground=COLORS['text'])
        style.configure('Horizontal.TScale', background=COLORS['bg_dark'], troughcolor=COLORS['bg_light'])

    def center_window(self):
        self.root.update_idletasks()
        w, h = self.root.winfo_width(), self.root.winfo_height()
        x = (self.root.winfo_screenwidth() - w) // 2
        y = (self.root.winfo_screenheight() - h) // 2
        self.root.geometry(f'{w}x{h}+{x}+{y}')

    def create_ui(self):
        # Main container
        main = tk.Frame(self.root, bg=COLORS['bg_dark'])
        main.pack(fill='both', expand=True)

        # Header
        self.create_header(main)

        # Content: Left panel + Right panel
        content = tk.Frame(main, bg=COLORS['bg_dark'])
        content.pack(fill='both', expand=True, padx=10, pady=5)

        # Left panel (scrollable)
        left_container = tk.Frame(content, bg=COLORS['bg_medium'], width=320)
        left_container.pack(side='left', fill='y', padx=(0, 10))
        left_container.pack_propagate(False)

        # Create scrollable left panel
        self.create_left_panel_scrollable(left_container)

        # Right panel
        right_panel = tk.Frame(content, bg=COLORS['bg_dark'])
        right_panel.pack(side='right', fill='both', expand=True)

        self.create_preview_area(right_panel)
        self.create_timeline(right_panel)

        # Bottom status bar
        self.create_status_bar(main)

    def create_header(self, parent):
        header = tk.Frame(parent, bg=COLORS['bg_medium'], height=50)
        header.pack(fill='x')
        header.pack_propagate(False)

        # Logo
        tk.Label(header, text="🎬 AI VIDEO STUDIO PRO",
                font=('Segoe UI', 16, 'bold'), fg=COLORS['accent'],
                bg=COLORS['bg_medium']).pack(side='left', padx=15, pady=10)

        tk.Label(header, text=f"v{VERSION}", font=('Segoe UI', 10),
                fg=COLORS['text_dim'], bg=COLORS['bg_medium']).pack(side='left')

        # Right buttons
        btn_frame = tk.Frame(header, bg=COLORS['bg_medium'])
        btn_frame.pack(side='right', padx=10)

        settings_btn = tk.Button(btn_frame, text="⚙️ Settings", font=('Segoe UI', 10),
                                fg=COLORS['text'], bg=COLORS['bg_light'], relief='flat',
                                cursor='hand2', command=self.open_settings)
        settings_btn.pack(side='right', padx=5)

        # Export button (prominent)
        export_btn = tk.Button(btn_frame, text="📤 Export", font=('Segoe UI', 11, 'bold'),
                              fg=COLORS['text'], bg=COLORS['accent'], relief='flat',
                              cursor='hand2', padx=15, command=self.open_export_dialog)
        export_btn.pack(side='right', padx=5)

    def create_left_panel_scrollable(self, container):
        # Canvas for scrolling
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

        # Enable mouse wheel scrolling
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")

        canvas.bind_all("<MouseWheel>", on_mousewheel)

        # Now create the content
        self.create_left_panel_content(self.left_frame)

    def create_left_panel_content(self, parent):
        # AUDIO Section
        self.create_section_header(parent, "🎙️ AUDIO / VOICE")

        audio_btn = tk.Button(parent, text="Select Audio File", font=('Segoe UI', 10),
                             fg=COLORS['text'], bg=COLORS['accent_blue'], relief='flat',
                             cursor='hand2', command=self.select_audio)
        audio_btn.pack(fill='x', padx=15, pady=5)

        self.audio_label = tk.Label(parent, text="No audio selected", font=('Segoe UI', 9),
                                   fg=COLORS['text_dim'], bg=COLORS['bg_medium'])
        self.audio_label.pack(padx=15, anchor='w')

        # IMAGES Section
        self.create_section_header(parent, "🖼️ IMAGES")

        for text, cmd in [("Add Images Folder", self.select_images_folder),
                          ("Add Individual Images", self.select_images),
                          ("Clear All Images", self.clear_images)]:
            btn = tk.Button(parent, text=text, font=('Segoe UI', 10),
                           fg=COLORS['text'], bg=COLORS['bg_light'], relief='flat',
                           cursor='hand2', command=cmd)
            btn.pack(fill='x', padx=15, pady=2)

        self.images_label = tk.Label(parent, text="0 images loaded", font=('Segoe UI', 9),
                                    fg=COLORS['text_dim'], bg=COLORS['bg_medium'])
        self.images_label.pack(padx=15, anchor='w', pady=(5, 0))

        # EFFECTS Section
        self.create_section_header(parent, "✨ EFFECTS")

        effects_frame = tk.Frame(parent, bg=COLORS['bg_medium'])
        effects_frame.pack(fill='x', padx=15)

        self.zoom_var = tk.BooleanVar(value=True)
        tk.Checkbutton(effects_frame, text="Ken Burns Zoom Effect", variable=self.zoom_var,
                      font=('Segoe UI', 10), fg=COLORS['text'], bg=COLORS['bg_medium'],
                      selectcolor=COLORS['bg_dark']).pack(anchor='w')

        zoom_slider_frame = tk.Frame(effects_frame, bg=COLORS['bg_medium'])
        zoom_slider_frame.pack(fill='x', pady=5)
        tk.Label(zoom_slider_frame, text="Zoom:", font=('Segoe UI', 9),
                fg=COLORS['text_dim'], bg=COLORS['bg_medium']).pack(side='left')
        self.zoom_slider = tk.Scale(zoom_slider_frame, from_=1.0, to=1.5, resolution=0.1,
                                   orient='horizontal', bg=COLORS['bg_medium'], fg=COLORS['text'],
                                   highlightthickness=0, troughcolor=COLORS['bg_dark'], length=150)
        self.zoom_slider.set(1.2)
        self.zoom_slider.pack(side='left', padx=5)

        self.fade_var = tk.BooleanVar(value=True)
        tk.Checkbutton(effects_frame, text="Fade Transitions", variable=self.fade_var,
                      font=('Segoe UI', 10), fg=COLORS['text'], bg=COLORS['bg_medium'],
                      selectcolor=COLORS['bg_dark']).pack(anchor='w')

        trans_frame = tk.Frame(effects_frame, bg=COLORS['bg_medium'])
        trans_frame.pack(fill='x', pady=5)
        tk.Label(trans_frame, text="Fade:", font=('Segoe UI', 9),
                fg=COLORS['text_dim'], bg=COLORS['bg_medium']).pack(side='left')
        self.trans_slider = tk.Scale(trans_frame, from_=0.5, to=2.0, resolution=0.5,
                                    orient='horizontal', bg=COLORS['bg_medium'], fg=COLORS['text'],
                                    highlightthickness=0, troughcolor=COLORS['bg_dark'], length=150)
        self.trans_slider.set(1.0)
        self.trans_slider.pack(side='left', padx=5)

        # OVERLAY Section
        self.create_section_header(parent, "🎨 OVERLAY / WATERMARK")

        overlay_btn = tk.Button(parent, text="Add Overlay Image", font=('Segoe UI', 10),
                               fg=COLORS['text'], bg=COLORS['bg_light'], relief='flat',
                               cursor='hand2', command=self.select_overlay)
        overlay_btn.pack(fill='x', padx=15, pady=5)

        self.overlay_label = tk.Label(parent, text="No overlay", font=('Segoe UI', 9),
                                     fg=COLORS['text_dim'], bg=COLORS['bg_medium'])
        self.overlay_label.pack(padx=15, anchor='w')

        # BACKGROUND MUSIC Section
        self.create_section_header(parent, "🎵 BACKGROUND MUSIC")

        music_btn = tk.Button(parent, text="Add Background Music", font=('Segoe UI', 10),
                             fg=COLORS['text'], bg=COLORS['bg_light'], relief='flat',
                             cursor='hand2', command=self.select_bg_music)
        music_btn.pack(fill='x', padx=15, pady=5)

        self.music_label = tk.Label(parent, text="No background music", font=('Segoe UI', 9),
                                   fg=COLORS['text_dim'], bg=COLORS['bg_medium'])
        self.music_label.pack(padx=15, anchor='w')

        # Music volume slider
        vol_frame = tk.Frame(parent, bg=COLORS['bg_medium'])
        vol_frame.pack(fill='x', padx=15, pady=5)
        tk.Label(vol_frame, text="Music Volume:", font=('Segoe UI', 9),
                fg=COLORS['text_dim'], bg=COLORS['bg_medium']).pack(side='left')
        self.music_vol_slider = tk.Scale(vol_frame, from_=0.0, to=1.0, resolution=0.1,
                                        orient='horizontal', bg=COLORS['bg_medium'], fg=COLORS['text'],
                                        highlightthickness=0, troughcolor=COLORS['bg_dark'], length=120)
        self.music_vol_slider.set(0.3)
        self.music_vol_slider.pack(side='left', padx=5)

        # INTELLIGENT SYNC Section
        self.create_section_header(parent, "🧠 INTELLIGENT SYNC")

        tk.Label(parent, text="AI matches images to voice automatically",
                font=('Segoe UI', 9), fg=COLORS['text_dim'], bg=COLORS['bg_medium']).pack(padx=15, anchor='w')

        sync_btn = tk.Button(parent, text="🧠 Start Intelligent Sync", font=('Segoe UI', 11, 'bold'),
                            fg=COLORS['text'], bg=COLORS['accent_orange'], relief='flat',
                            cursor='hand2', command=self.start_intelligent_sync)
        sync_btn.pack(fill='x', padx=15, pady=10)

        # Spacer
        tk.Frame(parent, bg=COLORS['bg_medium'], height=50).pack(fill='x')

    def create_section_header(self, parent, text):
        frame = tk.Frame(parent, bg=COLORS['bg_medium'])
        frame.pack(fill='x', padx=10, pady=(15, 5))

        tk.Label(frame, text=text, font=('Segoe UI', 11, 'bold'),
                fg=COLORS['text'], bg=COLORS['bg_medium']).pack(anchor='w')

    def create_preview_area(self, parent):
        preview_frame = tk.Frame(parent, bg=COLORS['bg_dark'])
        preview_frame.pack(fill='both', expand=True, pady=(0, 10))

        # Header with play button
        header = tk.Frame(preview_frame, bg=COLORS['bg_dark'])
        header.pack(fill='x')

        tk.Label(header, text="📺 PREVIEW", font=('Segoe UI', 12, 'bold'),
                fg=COLORS['text'], bg=COLORS['bg_dark']).pack(side='left')

        # Play button
        self.play_btn = tk.Button(header, text="▶️ Preview", font=('Segoe UI', 10),
                                 fg=COLORS['text'], bg=COLORS['bg_light'], relief='flat',
                                 cursor='hand2', command=self.preview_video)
        self.play_btn.pack(side='right', padx=5)

        # Preview canvas
        self.preview_canvas = tk.Canvas(preview_frame, bg=COLORS['bg_medium'],
                                        highlightthickness=1, highlightbackground=COLORS['border'])
        self.preview_canvas.pack(fill='both', expand=True, pady=5)

        self.preview_canvas.create_text(400, 200, text="Add images to see preview",
                                        font=('Segoe UI', 14), fill=COLORS['text_dim'])

    def create_timeline(self, parent):
        timeline_frame = tk.Frame(parent, bg=COLORS['bg_dark'])
        timeline_frame.pack(fill='x', pady=10)

        tk.Label(timeline_frame, text="📊 TIMELINE", font=('Segoe UI', 12, 'bold'),
                fg=COLORS['text'], bg=COLORS['bg_dark']).pack(anchor='w')

        # Timeline container with scroll
        timeline_container = tk.Frame(timeline_frame, bg=COLORS['timeline_bg'])
        timeline_container.pack(fill='x', pady=5)

        # Images track
        tk.Label(timeline_container, text="🖼️", font=('Segoe UI', 10),
                fg=COLORS['text_dim'], bg=COLORS['timeline_bg']).pack(anchor='w', padx=5)

        self.images_canvas = tk.Canvas(timeline_container, bg=COLORS['bg_medium'],
                                       height=60, highlightthickness=0)
        self.images_canvas.pack(fill='x', padx=5)

        # Audio track
        tk.Label(timeline_container, text="🎙️", font=('Segoe UI', 10),
                fg=COLORS['text_dim'], bg=COLORS['timeline_bg']).pack(anchor='w', padx=5, pady=(5, 0))

        self.audio_canvas = tk.Canvas(timeline_container, bg=COLORS['bg_medium'],
                                      height=40, highlightthickness=0)
        self.audio_canvas.pack(fill='x', padx=5)

        # Background music track
        tk.Label(timeline_container, text="🎵", font=('Segoe UI', 10),
                fg=COLORS['text_dim'], bg=COLORS['timeline_bg']).pack(anchor='w', padx=5, pady=(5, 0))

        self.music_canvas = tk.Canvas(timeline_container, bg=COLORS['bg_medium'],
                                      height=30, highlightthickness=0)
        self.music_canvas.pack(fill='x', padx=5, pady=(0, 5))

        # Log
        log_frame = tk.Frame(parent, bg=COLORS['bg_dark'])
        log_frame.pack(fill='x')

        tk.Label(log_frame, text="📝 LOG", font=('Segoe UI', 11, 'bold'),
                fg=COLORS['text'], bg=COLORS['bg_dark']).pack(anchor='w')

        self.log_text = scrolledtext.ScrolledText(log_frame, height=5, font=('Consolas', 9),
                                                  bg=COLORS['bg_medium'], fg=COLORS['text'],
                                                  insertbackground=COLORS['text'])
        self.log_text.pack(fill='x', pady=5)

        self.log("AI Video Studio Pro started")

    def create_status_bar(self, parent):
        status = tk.Frame(parent, bg=COLORS['bg_medium'], height=30)
        status.pack(fill='x', side='bottom')
        status.pack_propagate(False)

        self.status_label = tk.Label(status, text="Ready", font=('Segoe UI', 9),
                                    fg=COLORS['text_dim'], bg=COLORS['bg_medium'])
        self.status_label.pack(side='left', padx=10, pady=5)

        self.progress = ttk.Progressbar(status, mode='determinate', length=200)
        self.progress.pack(side='right', padx=10, pady=5)

    # ═══════════════════════════════════════════════════════════════
    # FILE SELECTION METHODS
    # ═══════════════════════════════════════════════════════════════

    def select_audio(self):
        path = filedialog.askopenfilename(
            title="Select Audio File",
            filetypes=[("Audio", "*.mp3 *.wav *.m4a *.flac *.ogg"), ("All", "*.*")]
        )
        if path:
            self.audio_path = path
            self.audio_duration = get_audio_duration(path)
            self.audio_label.config(text=f"✓ {os.path.basename(path)} ({format_time(self.audio_duration)})")
            self.log(f"Audio: {os.path.basename(path)} ({format_time(self.audio_duration)})")
            self.update_status(f"Audio loaded: {format_time(self.audio_duration)}")

            # Generate waveform
            self.waveform_data = get_audio_waveform_data(path)
            self.update_audio_timeline()

    def select_images_folder(self):
        folder = filedialog.askdirectory(title="Select Images Folder")
        if folder:
            exts = {'.jpg', '.jpeg', '.png', '.webp', '.bmp', '.gif'}
            new_imgs = sorted([os.path.join(folder, f) for f in os.listdir(folder)
                              if os.path.splitext(f)[1].lower() in exts])
            self.images.extend(new_imgs)
            self.images_label.config(text=f"✓ {len(self.images)} images loaded")
            self.log(f"Added {len(new_imgs)} images from folder")
            self.update_timeline_images()
            self.update_preview()

    def select_images(self):
        paths = filedialog.askopenfilenames(
            title="Select Images",
            filetypes=[("Images", "*.jpg *.jpeg *.png *.webp *.bmp *.gif")]
        )
        if paths:
            self.images.extend(paths)
            self.images_label.config(text=f"✓ {len(self.images)} images loaded")
            self.log(f"Added {len(paths)} images")
            self.update_timeline_images()
            self.update_preview()

    def clear_images(self):
        self.images = []
        self.images_label.config(text="0 images loaded")
        self.update_timeline_images()
        self.log("Images cleared")

    def select_overlay(self):
        path = filedialog.askopenfilename(
            title="Select Overlay",
            filetypes=[("Images", "*.png *.jpg *.jpeg")]
        )
        if path:
            self.overlay_path = path
            self.overlay_label.config(text=f"✓ {os.path.basename(path)}")
            self.log(f"Overlay: {os.path.basename(path)}")

    def select_bg_music(self):
        path = filedialog.askopenfilename(
            title="Select Background Music",
            filetypes=[("Audio", "*.mp3 *.wav *.m4a")]
        )
        if path:
            self.bg_music_path = path
            duration = get_audio_duration(path)
            self.music_label.config(text=f"✓ {os.path.basename(path)} ({format_time(duration)})")
            self.log(f"Background music: {os.path.basename(path)}")
            self.update_music_timeline()

    # ═══════════════════════════════════════════════════════════════
    # TIMELINE UPDATES
    # ═══════════════════════════════════════════════════════════════

    def update_timeline_images(self):
        self.images_canvas.delete('all')
        if not self.images:
            return

        width = self.images_canvas.winfo_width() or 800
        thumb_w = min(60, (width - 20) // min(len(self.images), 30))

        for i, img in enumerate(self.images[:30]):
            x = 5 + i * (thumb_w + 2)
            self.images_canvas.create_rectangle(x, 5, x + thumb_w, 55,
                                               fill=COLORS['bg_light'], outline=COLORS['border'])
            self.images_canvas.create_text(x + thumb_w//2, 30, text=str(i+1),
                                          font=('Segoe UI', 8), fill=COLORS['text'])

        if len(self.images) > 30:
            self.images_canvas.create_text(width - 40, 30, text=f"+{len(self.images)-30}",
                                          font=('Segoe UI', 9), fill=COLORS['text_dim'])

    def update_audio_timeline(self):
        self.audio_canvas.delete('all')
        if not self.waveform_data:
            if self.audio_path:
                self.audio_canvas.create_text(400, 20, text="Audio loaded",
                                             font=('Segoe UI', 9), fill=COLORS['text_dim'])
            return

        width = self.audio_canvas.winfo_width() or 800
        height = 40

        # Draw waveform
        points = []
        for i, amp in enumerate(self.waveform_data):
            x = int(i * width / len(self.waveform_data))
            y = int(height/2 - amp * height/2 * 0.9)
            points.append((x, y))

        for i, amp in enumerate(reversed(self.waveform_data)):
            x = int((len(self.waveform_data) - 1 - i) * width / len(self.waveform_data))
            y = int(height/2 + amp * height/2 * 0.9)
            points.append((x, y))

        if len(points) > 4:
            flat_points = [coord for point in points for coord in point]
            self.audio_canvas.create_polygon(flat_points, fill=COLORS['waveform'], outline='')

    def update_music_timeline(self):
        self.music_canvas.delete('all')
        if self.bg_music_path:
            width = self.music_canvas.winfo_width() or 800
            self.music_canvas.create_rectangle(5, 5, width-5, 25,
                                              fill=COLORS['accent_orange'], outline='')
            self.music_canvas.create_text(width//2, 15, text="🎵 Background Music",
                                         font=('Segoe UI', 8), fill=COLORS['text'])

    def update_preview(self):
        self.preview_canvas.delete('all')

        if self.images and PIL_AVAILABLE:
            try:
                img = Image.open(self.images[0])
                canvas_w = self.preview_canvas.winfo_width() or 600
                canvas_h = self.preview_canvas.winfo_height() or 350

                ratio = min(canvas_w / img.width, canvas_h / img.height) * 0.9
                new_size = (int(img.width * ratio), int(img.height * ratio))
                img = img.resize(new_size, Image.Resampling.LANCZOS)

                self.preview_photo = ImageTk.PhotoImage(img)
                self.preview_canvas.create_image(canvas_w//2, canvas_h//2, image=self.preview_photo)
            except Exception as e:
                self.preview_canvas.create_text(300, 175, text=f"Preview error: {e}",
                                               font=('Segoe UI', 10), fill=COLORS['error'])
        else:
            self.preview_canvas.create_text(300, 175, text="Add images to see preview",
                                           font=('Segoe UI', 14), fill=COLORS['text_dim'])

    def preview_video(self):
        """Preview images as slideshow"""
        if not self.images:
            messagebox.showinfo("Preview", "Add images first to preview!")
            return

        # Create preview window
        preview_win = tk.Toplevel(self.root)
        preview_win.title("Video Preview")
        preview_win.geometry("960x540")
        preview_win.configure(bg='black')
        preview_win.transient(self.root)

        # Preview canvas
        preview_canvas = tk.Canvas(preview_win, bg='black', highlightthickness=0)
        preview_canvas.pack(fill='both', expand=True)

        # Control frame
        controls = tk.Frame(preview_win, bg=COLORS['bg_medium'])
        controls.pack(fill='x')

        self.preview_playing = False
        self.preview_index = 0

        def show_image(idx):
            if idx >= len(self.images):
                idx = 0
            self.preview_index = idx

            try:
                img = Image.open(self.images[idx])
                canvas_w = preview_canvas.winfo_width() or 960
                canvas_h = preview_canvas.winfo_height() or 500

                ratio = min(canvas_w / img.width, canvas_h / img.height)
                new_size = (int(img.width * ratio), int(img.height * ratio))
                img = img.resize(new_size, Image.Resampling.LANCZOS)

                self.preview_tk_img = ImageTk.PhotoImage(img)
                preview_canvas.delete('all')
                preview_canvas.create_image(canvas_w//2, canvas_h//2, image=self.preview_tk_img)
                preview_canvas.create_text(canvas_w//2, canvas_h - 20,
                    text=f"Image {idx+1} / {len(self.images)}",
                    fill='white', font=('Segoe UI', 10))
            except Exception as e:
                preview_canvas.create_text(480, 270, text=f"Error: {e}", fill='red')

        def play_slideshow():
            if self.preview_playing:
                self.preview_index = (self.preview_index + 1) % len(self.images)
                show_image(self.preview_index)
                # Duration per image
                dur = int((self.audio_duration / len(self.images)) * 1000) if self.audio_duration else 2000
                dur = min(dur, 3000)  # Max 3 seconds per image in preview
                preview_win.after(dur, play_slideshow)

        def toggle_play():
            self.preview_playing = not self.preview_playing
            play_btn.config(text="⏸️ Pause" if self.preview_playing else "▶️ Play")
            if self.preview_playing:
                play_slideshow()

        def prev_img():
            self.preview_index = (self.preview_index - 1) % len(self.images)
            show_image(self.preview_index)

        def next_img():
            self.preview_index = (self.preview_index + 1) % len(self.images)
            show_image(self.preview_index)

        tk.Button(controls, text="⏮️", font=('Segoe UI', 12),
                 bg=COLORS['bg_light'], fg=COLORS['text'], relief='flat',
                 command=prev_img).pack(side='left', padx=5, pady=5)

        play_btn = tk.Button(controls, text="▶️ Play", font=('Segoe UI', 11),
                            bg=COLORS['accent'], fg=COLORS['text'], relief='flat',
                            width=10, command=toggle_play)
        play_btn.pack(side='left', padx=5, pady=5)

        tk.Button(controls, text="⏭️", font=('Segoe UI', 12),
                 bg=COLORS['bg_light'], fg=COLORS['text'], relief='flat',
                 command=next_img).pack(side='left', padx=5, pady=5)

        tk.Button(controls, text="✖ Close", font=('Segoe UI', 10),
                 bg=COLORS['bg_light'], fg=COLORS['text'], relief='flat',
                 command=preview_win.destroy).pack(side='right', padx=5, pady=5)

        # Show first image
        preview_win.after(100, lambda: show_image(0))

    # ═══════════════════════════════════════════════════════════════
    # LOGGING & STATUS
    # ═══════════════════════════════════════════════════════════════

    def log(self, msg):
        ts = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert('end', f"[{ts}] {msg}\n")
        self.log_text.see('end')

    def update_status(self, msg):
        self.status_label.config(text=msg)

    def update_progress(self, val, max_val=100):
        self.progress['maximum'] = max_val
        self.progress['value'] = val
        self.root.update_idletasks()

    # ═══════════════════════════════════════════════════════════════
    # EXPORT
    # ═══════════════════════════════════════════════════════════════

    def open_export_dialog(self):
        if not self.images:
            messagebox.showerror("Error", "Please add images first!")
            return
        if not self.audio_path:
            messagebox.showerror("Error", "Please select an audio file!")
            return

        dialog = ExportDialog(self.root, self.config, self.audio_duration,
                             self.images[0] if self.images else None)
        result = dialog.show()

        if result:
            self.start_export(result)

    def start_export(self, settings):
        self.log(f"Exporting to: {settings['output_path']}")
        self.log(f"Settings: {settings['resolution']}, {settings['codec']}, {settings['bitrate']}, {settings['fps']}fps")

        # Run in thread
        thread = threading.Thread(target=self.export_video, args=(settings,))
        thread.start()

    def export_video(self, settings):
        try:
            self.root.after(0, lambda: self.update_status("Exporting..."))

            # Calculate durations
            dur_per_img = self.audio_duration / len(self.images)
            durations = [dur_per_img] * len(self.images)

            def progress_cb(curr, total, msg):
                self.root.after(0, lambda: self.update_progress(curr, total))
                self.root.after(0, lambda: self.log(msg))

            success = VideoProcessor.create_video(
                images=self.images,
                durations=durations,
                audio_path=self.audio_path,
                output_path=settings['output_path'],
                resolution=settings['resolution'],
                bitrate=settings['bitrate'],
                codec=settings['codec'],
                fps=settings['fps'],
                use_gpu=settings['use_gpu'],
                zoom_enabled=self.zoom_var.get(),
                zoom_intensity=self.zoom_slider.get(),
                fade_enabled=self.fade_var.get(),
                fade_duration=self.trans_slider.get(),
                bg_music_path=self.bg_music_path,
                bg_music_volume=self.music_vol_slider.get(),
                overlay_path=self.overlay_path,
                progress_callback=progress_cb
            )

            if success:
                self.root.after(0, lambda: self.log(f"✓ Export complete: {settings['output_path']}"))
                self.root.after(0, lambda: messagebox.showinfo("Success",
                    f"Video exported successfully!\n\n{settings['output_path']}"))
            else:
                self.root.after(0, lambda: messagebox.showerror("Error", "Export failed!"))

        except Exception as e:
            self.root.after(0, lambda: self.log(f"✗ Error: {e}"))
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))

        finally:
            self.root.after(0, lambda: self.update_progress(0))
            self.root.after(0, lambda: self.update_status("Ready"))

    # ═══════════════════════════════════════════════════════════════
    # INTELLIGENT SYNC
    # ═══════════════════════════════════════════════════════════════

    def start_intelligent_sync(self):
        if not self.images:
            messagebox.showerror("Error", "Please add images!")
            return
        if not self.audio_path:
            messagebox.showerror("Error", "Please select audio!")
            return

        api_key = self.config['api_keys'].get('openai', '')
        if not api_key:
            messagebox.showerror("API Key Required",
                "OpenAI API key needed for Intelligent Sync.\n\nGo to Settings to add your key.")
            return

        # Ask for output
        output = filedialog.asksaveasfilename(
            title="Save Synced Video",
            defaultextension=".mp4",
            filetypes=[("MP4", "*.mp4")]
        )

        if not output:
            return

        thread = threading.Thread(target=self.intelligent_sync_process, args=(output, api_key))
        thread.start()

    def intelligent_sync_process(self, output_path, api_key):
        try:
            client = OpenAIClient(api_key)

            # Step 1: Transcribe
            self.root.after(0, lambda: self.log("Step 1: Transcribing audio..."))
            self.root.after(0, lambda: self.update_status("Transcribing..."))

            transcription = client.transcribe(self.audio_path)
            if not transcription:
                raise Exception("Transcription failed!")

            self.root.after(0, lambda: self.log(f"✓ Transcription: {transcription.get('text', '')[:80]}..."))

            # Parse segments
            segments = []
            words = transcription.get('words', [])
            if words:
                curr = {'text': '', 'start': words[0]['start'], 'end': 0}
                for w in words:
                    curr['text'] += w['word'] + ' '
                    curr['end'] = w['end']
                    if w['word'].rstrip().endswith(('.', '!', '?', ',')) and curr['end'] - curr['start'] >= 1.5:
                        segments.append({'text': curr['text'].strip(), 'start': curr['start'], 'end': curr['end']})
                        curr = {'text': '', 'start': w['end'], 'end': 0}
                if curr['text']:
                    segments.append({'text': curr['text'].strip(), 'start': curr['start'], 'end': curr['end']})

            self.root.after(0, lambda: self.log(f"✓ {len(segments)} transcript segments"))

            # Step 2: Analyze images
            self.root.after(0, lambda: self.log("Step 2: Analyzing images..."))
            self.root.after(0, lambda: self.update_status("Analyzing images..."))

            image_infos = []
            for i, img in enumerate(self.images):
                self.root.after(0, lambda i=i: self.update_progress(i, len(self.images)))
                keywords = client.analyze_image(img)
                image_infos.append(keywords)
                time.sleep(0.3)

            self.root.after(0, lambda: self.log(f"✓ Analyzed {len(image_infos)} images"))

            # Step 3: Match
            self.root.after(0, lambda: self.log("Step 3: AI matching..."))
            self.root.after(0, lambda: self.update_status("Matching..."))

            matches = client.match_images(segments, image_infos)
            if not matches:
                matches = [{'segment_id': i, 'image_id': i % len(self.images)} for i in range(len(segments))]

            self.root.after(0, lambda: self.log(f"✓ Created {len(matches)} matches"))

            # Build video
            video_images = []
            video_durations = []

            for m in matches:
                seg_id = m['segment_id']
                img_id = m['image_id']
                if seg_id < len(segments) and img_id < len(self.images):
                    seg = segments[seg_id]
                    video_images.append(self.images[img_id])
                    video_durations.append(seg['end'] - seg['start'])

            # Step 4: Create video
            self.root.after(0, lambda: self.log("Step 4: Creating video..."))
            self.root.after(0, lambda: self.update_status("Creating video..."))

            success = VideoProcessor.create_video(
                images=video_images,
                durations=video_durations,
                audio_path=self.audio_path,
                output_path=output_path,
                zoom_enabled=self.zoom_var.get(),
                zoom_intensity=self.zoom_slider.get(),
                fade_enabled=self.fade_var.get(),
                fade_duration=self.trans_slider.get()
            )

            if success:
                self.root.after(0, lambda: self.log(f"✓ Synced video: {output_path}"))
                self.root.after(0, lambda: messagebox.showinfo("Success",
                    f"Intelligent sync complete!\n\n{output_path}"))
            else:
                raise Exception("Video creation failed!")

        except Exception as e:
            self.root.after(0, lambda: self.log(f"✗ Error: {e}"))
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))

        finally:
            self.root.after(0, lambda: self.update_progress(0))
            self.root.after(0, lambda: self.update_status("Ready"))

    # ═══════════════════════════════════════════════════════════════
    # SETTINGS
    # ═══════════════════════════════════════════════════════════════

    def open_settings(self):
        win = tk.Toplevel(self.root)
        win.title("Settings")
        win.geometry("450x300")
        win.configure(bg=COLORS['bg_dark'])
        win.transient(self.root)
        win.grab_set()

        tk.Label(win, text="⚙️ Settings", font=('Segoe UI', 16, 'bold'),
                fg=COLORS['accent'], bg=COLORS['bg_dark']).pack(pady=15)

        # API Key
        frame = tk.LabelFrame(win, text="API Keys", font=('Segoe UI', 10, 'bold'),
                             fg=COLORS['text'], bg=COLORS['bg_dark'])
        frame.pack(fill='x', padx=20, pady=10)

        tk.Label(frame, text="OpenAI API Key:", fg=COLORS['text_dim'],
                bg=COLORS['bg_dark']).pack(anchor='w', padx=10, pady=(10, 0))

        api_entry = tk.Entry(frame, width=45, show='*', bg=COLORS['bg_light'],
                            fg=COLORS['text'], insertbackground=COLORS['text'])
        api_entry.insert(0, self.config['api_keys'].get('openai', ''))
        api_entry.pack(padx=10, pady=5)

        def save():
            self.config['api_keys']['openai'] = api_entry.get()
            save_config(self.config)
            self.log("Settings saved!")
            win.destroy()

        tk.Button(win, text="Save", font=('Segoe UI', 11), fg=COLORS['text'],
                 bg=COLORS['accent'], relief='flat', command=save).pack(pady=20)

    def run(self):
        self.root.mainloop()


# ═══════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    app = AIVideoStudioApp()
    app.run()
