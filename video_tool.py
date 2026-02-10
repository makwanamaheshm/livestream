#!/usr/bin/env python3
"""
==============================================
    AI VIDEO GENERATOR TOOL
==============================================
Generates videos using:
- ElevenLabs API (Voice)
- Ideogram / Gemini API (Images)
- FFmpeg (Video)

Usage:
    python video_tool.py --setup          # Setup API keys
    python video_tool.py --generate       # Generate video interactively
    python video_tool.py --script "text"  # Generate with script
==============================================
"""

import os
import sys
import json
import requests
import subprocess
import time
import argparse
import base64
from pathlib import Path
from datetime import datetime

# ============================================
# CONFIGURATION
# ============================================

CONFIG_FILE = Path(__file__).parent / "config.json"
DEFAULT_OUTPUT = Path(__file__).parent / "output"

def load_config():
    """Load configuration from config.json"""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return None

def save_config(config):
    """Save configuration to config.json"""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)
    print(f"Config saved to: {CONFIG_FILE}")

def setup_wizard():
    """Interactive setup wizard for API keys"""
    print("\n" + "="*50)
    print("    AI VIDEO GENERATOR - SETUP WIZARD")
    print("="*50 + "\n")

    config = load_config() or {
        "api_keys": {},
        "settings": {
            "image_provider": "ideogram",
            "video_resolution": "1920x1080",
            "images_count": 6,
            "output_folder": "output"
        }
    }

    print("Enter your API keys (press Enter to skip/keep existing):\n")

    # ElevenLabs
    current = config["api_keys"].get("elevenlabs", "")
    display = current[:10] + "..." if current and current != "YOUR_ELEVENLABS_API_KEY" else "Not set"
    key = input(f"1. ElevenLabs API Key [{display}]: ").strip()
    if key:
        config["api_keys"]["elevenlabs"] = key

    current = config["api_keys"].get("elevenlabs_voice_id", "")
    display = current if current and current != "YOUR_VOICE_ID" else "Not set"
    voice_id = input(f"2. ElevenLabs Voice ID [{display}]: ").strip()
    if voice_id:
        config["api_keys"]["elevenlabs_voice_id"] = voice_id

    # Ideogram
    current = config["api_keys"].get("ideogram", "")
    display = current[:10] + "..." if current and current != "YOUR_IDEOGRAM_API_KEY" else "Not set"
    key = input(f"3. Ideogram API Key [{display}]: ").strip()
    if key:
        config["api_keys"]["ideogram"] = key

    # Gemini
    current = config["api_keys"].get("gemini", "")
    display = current[:10] + "..." if current and current != "YOUR_GEMINI_API_KEY" else "Not set"
    key = input(f"4. Gemini API Key [{display}]: ").strip()
    if key:
        config["api_keys"]["gemini"] = key

    # Image provider choice
    print("\n5. Choose Image Provider:")
    print("   [1] Ideogram (recommended)")
    print("   [2] Gemini")
    choice = input("   Enter choice [1]: ").strip()
    if choice == "2":
        config["settings"]["image_provider"] = "gemini"
    else:
        config["settings"]["image_provider"] = "ideogram"

    # Number of images
    num = input(f"\n6. Number of images to generate [6]: ").strip()
    if num.isdigit():
        config["settings"]["images_count"] = int(num)

    save_config(config)
    print("\n Setup complete! You can now generate videos.")
    print("   Run: python video_tool.py --generate\n")

# ============================================
# VOICE GENERATION (ElevenLabs)
# ============================================

def generate_voice(text, output_path, config):
    """Generate voice using ElevenLabs API"""
    print("\n Generating voice with ElevenLabs...")

    api_key = config["api_keys"].get("elevenlabs")
    voice_id = config["api_keys"].get("elevenlabs_voice_id")

    if not api_key or api_key == "YOUR_ELEVENLABS_API_KEY":
        print(" ElevenLabs API key not configured!")
        return False

    if not voice_id or voice_id == "YOUR_VOICE_ID":
        print(" ElevenLabs Voice ID not configured!")
        return False

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": api_key
    }

    data = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.5
        }
    }

    try:
        response = requests.post(url, json=data, headers=headers, timeout=120)

        if response.status_code == 200:
            with open(output_path, 'wb') as f:
                f.write(response.content)
            print(f" Voice saved: {output_path}")
            return True
        else:
            print(f" ElevenLabs Error: {response.status_code}")
            print(f"   {response.text[:200]}")
            return False
    except Exception as e:
        print(f" Error: {e}")
        return False

# ============================================
# IMAGE GENERATION
# ============================================

def generate_images_ideogram(prompts, output_dir, config):
    """Generate images using Ideogram API"""
    print("\n Generating images with Ideogram...")

    api_key = config["api_keys"].get("ideogram")
    if not api_key or api_key == "YOUR_IDEOGRAM_API_KEY":
        print(" Ideogram API key not configured!")
        return []

    url = "https://api.ideogram.ai/generate"
    headers = {
        "Api-Key": api_key,
        "Content-Type": "application/json"
    }

    generated_images = []

    for i, prompt in enumerate(prompts):
        print(f"   Generating image {i+1}/{len(prompts)}...", end=" ", flush=True)

        data = {
            "image_request": {
                "prompt": prompt,
                "aspect_ratio": "ASPECT_16_9",
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
                                image_path = output_dir / f"image_{i+1}.png"
                                with open(image_path, 'wb') as f:
                                    f.write(img_response.content)
                                generated_images.append(str(image_path))
                                print("Done!")
                                break

                print(f"Retry {attempt+1}...", end=" ", flush=True)
                time.sleep(2)

            except Exception as e:
                print(f"Error: {e}")
                time.sleep(2)

        time.sleep(1)

    return generated_images

def generate_images_gemini(prompts, output_dir, config):
    """Generate images using Gemini API"""
    print("\n Generating images with Gemini...")

    api_key = config["api_keys"].get("gemini")
    if not api_key or api_key == "YOUR_GEMINI_API_KEY":
        print(" Gemini API key not configured!")
        return []

    url = f"https://generativelanguage.googleapis.com/v1beta/models/imagen-3.0-generate-001:generateImages?key={api_key}"

    generated_images = []

    for i, prompt in enumerate(prompts):
        print(f"   Generating image {i+1}/{len(prompts)}...", end=" ", flush=True)

        data = {
            "prompt": prompt,
            "number_of_images": 1,
            "aspect_ratio": "16:9"
        }

        try:
            response = requests.post(url, json=data, headers={"Content-Type": "application/json"}, timeout=60)

            if response.status_code == 200:
                result = response.json()
                if 'generatedImages' in result and len(result['generatedImages']) > 0:
                    image_data = result['generatedImages'][0].get('image', {}).get('imageBytes', '')
                    if image_data:
                        image_path = output_dir / f"image_{i+1}.png"
                        with open(image_path, 'wb') as f:
                            f.write(base64.b64decode(image_data))
                        generated_images.append(str(image_path))
                        print("Done!")
                        continue

            print(f"Failed: {response.status_code}")

        except Exception as e:
            print(f"Error: {e}")

        time.sleep(1)

    return generated_images

def generate_placeholder_images(num_images, output_dir):
    """Generate placeholder images if API fails"""
    print("\n Creating placeholder images...")

    try:
        from PIL import Image, ImageDraw
    except ImportError:
        print(" PIL not installed. Run: pip install Pillow")
        return []

    colors = [
        (139, 90, 43), (85, 65, 55), (160, 120, 70),
        (70, 50, 40), (180, 150, 100), (100, 80, 60),
    ]

    images = []
    for i in range(num_images):
        img = Image.new('RGB', (1920, 1080), colors[i % len(colors)])
        draw = ImageDraw.Draw(img)
        text = f"Scene {i+1}"
        bbox = draw.textbbox((0, 0), text)
        x = (1920 - (bbox[2] - bbox[0])) // 2
        y = (1080 - (bbox[3] - bbox[1])) // 2
        draw.text((x, y), text, fill=(255, 245, 220))

        image_path = output_dir / f"image_{i+1}.png"
        img.save(image_path)
        images.append(str(image_path))
        print(f"   Placeholder {i+1} created")

    return images

# ============================================
# VIDEO CREATION
# ============================================

def get_audio_duration(audio_path):
    """Get audio duration using ffprobe"""
    cmd = [
        'ffprobe', '-v', 'error',
        '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1',
        str(audio_path)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return float(result.stdout.strip())

def create_video(images, audio_path, output_path):
    """Create video from images and audio using FFmpeg"""
    print("\n Creating video with FFmpeg...")

    duration = get_audio_duration(audio_path)
    print(f"   Audio duration: {duration:.2f}s")

    num_images = len(images)
    image_duration = duration / num_images
    print(f"   Each image: {image_duration:.2f}s")

    # Create file list
    filelist_path = output_path.parent / "filelist.txt"
    with open(filelist_path, 'w') as f:
        for img in images:
            f.write(f"file '{img}'\n")
            f.write(f"duration {image_duration}\n")
        f.write(f"file '{images[-1]}'\n")

    # FFmpeg command
    cmd = [
        'ffmpeg', '-y',
        '-f', 'concat', '-safe', '0',
        '-i', str(filelist_path),
        '-i', str(audio_path),
        '-vf', 'scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2',
        '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
        '-c:a', 'aac', '-shortest',
        '-movflags', '+faststart',
        str(output_path)
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        print(f" Video created: {output_path}")
        return True
    else:
        print(f" FFmpeg Error: {result.stderr[:300]}")
        return False

# ============================================
# PROMPT GENERATOR
# ============================================

def generate_image_prompts(script, num_images):
    """Generate image prompts based on script content"""
    # Simple keyword-based prompt generation
    prompts = []

    # Split script into chunks
    words = script.split()
    chunk_size = len(words) // num_images

    base_style = "cinematic, high quality, detailed, professional photography"

    for i in range(num_images):
        start = i * chunk_size
        end = start + chunk_size if i < num_images - 1 else len(words)
        chunk = ' '.join(words[start:end])

        # Extract key themes
        if any(word in chunk.lower() for word in ['1920', 'twenty', 'vintage', 'old']):
            prompt = f"Vintage 1920s scene, sepia toned, historical, {base_style}"
        elif any(word in chunk.lower() for word in ['morning', 'wake', 'breakfast', 'coffee']):
            prompt = f"Cozy morning scene, warm lighting, nostalgic atmosphere, {base_style}"
        elif any(word in chunk.lower() for word in ['night', 'dim', 'dark', 'sleep']):
            prompt = f"Peaceful night scene, soft ambient lighting, relaxing mood, {base_style}"
        elif any(word in chunk.lower() for word in ['city', 'street', 'car']):
            prompt = f"Vintage city street scene, classic cars, urban atmosphere, {base_style}"
        elif any(word in chunk.lower() for word in ['home', 'house', 'room', 'kitchen']):
            prompt = f"Vintage interior scene, warm cozy home, rustic charm, {base_style}"
        else:
            prompt = f"Atmospheric scene, storytelling mood, artistic composition, {base_style}"

        prompts.append(prompt)

    return prompts

# ============================================
# MAIN GENERATOR
# ============================================

def generate_video(script, custom_prompts=None):
    """Main video generation function"""
    config = load_config()

    if not config:
        print("\n Config not found! Run setup first:")
        print("   python video_tool.py --setup\n")
        return

    # Create output directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = DEFAULT_OUTPUT / timestamp
    output_dir.mkdir(parents=True, exist_ok=True)

    print("\n" + "="*50)
    print("    AI VIDEO GENERATOR")
    print("="*50)
    print(f"\n Output folder: {output_dir}")

    # Paths
    audio_path = output_dir / "narration.mp3"
    video_path = output_dir / "final_video.mp4"

    # Step 1: Generate Voice
    print("\n" + "-"*50)
    print(" STEP 1: Voice Generation")
    print("-"*50)

    if not generate_voice(script, audio_path, config):
        print("\n Failed to generate voice. Exiting.")
        return

    # Step 2: Generate Images
    print("\n" + "-"*50)
    print(" STEP 2: Image Generation")
    print("-"*50)

    num_images = config["settings"].get("images_count", 6)

    if custom_prompts:
        prompts = custom_prompts
    else:
        prompts = generate_image_prompts(script, num_images)
        print(f"   Auto-generated {len(prompts)} image prompts")

    provider = config["settings"].get("image_provider", "ideogram")

    if provider == "ideogram":
        images = generate_images_ideogram(prompts, output_dir, config)
    else:
        images = generate_images_gemini(prompts, output_dir, config)

    # Fallback to placeholders
    if len(images) < 3:
        print("\n Image API failed. Using placeholders...")
        images = generate_placeholder_images(num_images, output_dir)

    if not images:
        print("\n No images generated. Exiting.")
        return

    # Step 3: Create Video
    print("\n" + "-"*50)
    print(" STEP 3: Video Creation")
    print("-"*50)

    if create_video(images, audio_path, video_path):
        # Get video info
        size = video_path.stat().st_size / (1024 * 1024)
        duration = get_audio_duration(audio_path)

        print("\n" + "="*50)
        print("    VIDEO GENERATION COMPLETE!")
        print("="*50)
        print(f"\n   Video: {video_path}")
        print(f"   Size: {size:.2f} MB")
        print(f"   Duration: {duration:.2f} seconds")
        print(f"   Resolution: 1920x1080")
        print("\n" + "="*50 + "\n")
    else:
        print("\n Video generation failed.")

def interactive_mode():
    """Interactive video generation mode"""
    config = load_config()

    if not config or config["api_keys"].get("elevenlabs") == "YOUR_ELEVENLABS_API_KEY":
        print("\n Please run setup first: python video_tool.py --setup\n")
        return

    print("\n" + "="*50)
    print("    AI VIDEO GENERATOR - Interactive Mode")
    print("="*50)

    print("\n Enter your script (paste text, then press Enter twice to finish):\n")

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
        print("\n No script provided. Exiting.")
        return

    print(f"\n Script length: {len(script)} characters")

    # Ask for custom prompts
    use_custom = input("\n Do you want to provide custom image prompts? (y/N): ").strip().lower()

    custom_prompts = None
    if use_custom == 'y':
        num = config["settings"].get("images_count", 6)
        print(f"\n Enter {num} image prompts (one per line):")
        custom_prompts = []
        for i in range(num):
            prompt = input(f"   {i+1}. ").strip()
            if prompt:
                custom_prompts.append(prompt)

        if len(custom_prompts) < num:
            print(f"\n Only {len(custom_prompts)} prompts provided. Auto-generating rest...")
            custom_prompts = None

    confirm = input("\n Start video generation? (Y/n): ").strip().lower()
    if confirm == 'n':
        print("\n Cancelled.")
        return

    generate_video(script, custom_prompts)

# ============================================
# CLI
# ============================================

def main():
    parser = argparse.ArgumentParser(
        description="AI Video Generator Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python video_tool.py --setup              # Configure API keys
  python video_tool.py --generate           # Interactive mode
  python video_tool.py --script "Your text" # Direct generation
  python video_tool.py --config             # Show current config
        """
    )

    parser.add_argument('--setup', action='store_true', help='Run setup wizard')
    parser.add_argument('--generate', action='store_true', help='Generate video interactively')
    parser.add_argument('--script', type=str, help='Script text for video')
    parser.add_argument('--config', action='store_true', help='Show current configuration')

    args = parser.parse_args()

    if args.setup:
        setup_wizard()
    elif args.config:
        config = load_config()
        if config:
            print("\nCurrent Configuration:")
            print(json.dumps(config, indent=2))
        else:
            print("\nNo configuration found. Run --setup first.")
    elif args.script:
        generate_video(args.script)
    elif args.generate:
        interactive_mode()
    else:
        # Default: show help
        parser.print_help()
        print("\n Quick Start:")
        print("  1. python video_tool.py --setup")
        print("  2. python video_tool.py --generate\n")

if __name__ == "__main__":
    main()
