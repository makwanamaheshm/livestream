#!/usr/bin/env python3
"""
Video Generator Script
- Generates voice using ElevenLabs API
- Generates images using Ideogram API
- Combines into video using FFmpeg
"""

import os
import requests
import json
import subprocess
import base64
import time
from pathlib import Path

# Configuration
ELEVENLABS_API_KEY = "sk_fc848225ae9eea44da327054ae822165886fe87ece55287c"
ELEVENLABS_VOICE_ID = "G17SuINrv2H9FC6nvetn"
IDEOGRAM_API_KEY = "_32w9YNspQiaX5gi3G0o7MiUsMUJxl0F8MMN95m7s2VjWjMkySet4ErNTbRdh2t510CE8a7lro5RcT52WgQdYw"

# Script for the video
SCRIPT = """Hey guys, tonight we step back exactly one hundred years into a world that looks deceptively familiar in photographs but would feel utterly alien the moment you opened your eyes inside it. Imagine waking up tomorrow morning and discovering that your smartphone is gone, your thermostat doesn't exist, and the bathroom you stumble toward might actually be a small wooden shed fifty feet from your back door. This is America in the 1920s—the Roaring Twenties, they'll call it later, but right now, in this moment, you're just trying to survive until breakfast without freezing, tripping over a chamber pot, or accidentally poisoning yourself with the patent medicine you bought last week. You probably won't last a day without complaining, honestly. The coffee is weak, the mornings are brutal, and nobody has invented the snooze button yet. So, before you get comfortable, take a moment to like the video and subscribe—but only if you genuinely enjoy what I do here. Drop a comment telling me where you're listening from and what time it is where you are—I love seeing how this little community stretches across time zones, all of us drifting off together. Now, dim the lights, maybe turn on a fan for that soft background hum, and let's ease into tonight's journey together."""

# Image prompts for 1920s America theme (optimized for Ideogram)
IMAGE_PROMPTS = [
    "Vintage 1920s American city street with Model T Ford cars, people in period clothing, sepia toned historical photograph, cinematic lighting",
    "1920s American wooden farmhouse at dawn, outdoor shed bathroom in distance, morning fog, vintage photography style, nostalgic atmosphere",
    "Roaring Twenties jazz club interior, people dancing Charleston, art deco decorations, warm golden lighting, vintage glamour",
    "1920s American kitchen interior, cast iron stove, percolator coffee pot, morning sunlight through window, rustic charm",
    "Old patent medicine bottles and vintage advertisements from 1920s America, still life composition, antique aesthetic",
    "1920s bedroom with oil lamp on nightstand, vintage iron bed frame, cozy warm atmosphere, historical interior"
]

# Output directory
OUTPUT_DIR = Path("/home/user/livestream/output")
OUTPUT_DIR.mkdir(exist_ok=True)

def generate_voice(text, output_path):
    """Generate voice using ElevenLabs API"""
    print("🎙️ Generating voice with ElevenLabs...")

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}"

    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": ELEVENLABS_API_KEY
    }

    data = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.5
        }
    }

    response = requests.post(url, json=data, headers=headers)

    if response.status_code == 200:
        with open(output_path, 'wb') as f:
            f.write(response.content)
        print(f"✅ Voice saved to: {output_path}")
        return True
    else:
        print(f"❌ ElevenLabs Error: {response.status_code}")
        print(response.text)
        return False

def generate_images_ideogram(prompts, output_dir):
    """Generate images using Ideogram API"""
    print("🖼️ Generating images with Ideogram...")

    url = "https://api.ideogram.ai/generate"

    headers = {
        "Api-Key": IDEOGRAM_API_KEY,
        "Content-Type": "application/json"
    }

    generated_images = []

    for i, prompt in enumerate(prompts):
        print(f"  Generating image {i+1}/{len(prompts)}...")

        data = {
            "image_request": {
                "prompt": prompt,
                "aspect_ratio": "ASPECT_16_9",
                "model": "V_2",
                "magic_prompt_option": "AUTO",
                "style_type": "REALISTIC"
            }
        }

        try:
            response = requests.post(url, json=data, headers=headers, timeout=120)

            if response.status_code == 200:
                result = response.json()

                # Get image URL from response
                if 'data' in result and len(result['data']) > 0:
                    image_url = result['data'][0].get('url')
                    if image_url:
                        # Download the image
                        img_response = requests.get(image_url, timeout=60)
                        if img_response.status_code == 200:
                            image_path = output_dir / f"image_{i+1}.png"
                            with open(image_path, 'wb') as f:
                                f.write(img_response.content)
                            generated_images.append(str(image_path))
                            print(f"  ✅ Image {i+1} saved")
                            continue

            print(f"  ⚠️ Ideogram response: {response.status_code}")
            try:
                print(f"     {response.json()}")
            except:
                print(f"     {response.text[:300]}")

        except Exception as e:
            print(f"  ⚠️ Error generating image {i+1}: {e}")

        # Delay between requests to avoid rate limiting
        time.sleep(2)

    return generated_images

def generate_placeholder_images(num_images, output_dir):
    """Generate placeholder images if API fails"""
    print("🖼️ Creating placeholder images...")
    from PIL import Image, ImageDraw, ImageFont

    colors = [
        (139, 90, 43),   # Brown - vintage
        (85, 65, 55),    # Dark brown
        (160, 120, 70),  # Tan
        (70, 50, 40),    # Dark vintage
        (180, 150, 100), # Light sepia
        (100, 80, 60),   # Medium brown
    ]

    texts = [
        "1920s America",
        "The Roaring Twenties",
        "A World Without Technology",
        "Morning in 1920",
        "Patent Medicine Era",
        "Life 100 Years Ago"
    ]

    images = []
    for i in range(num_images):
        img = Image.new('RGB', (1920, 1080), colors[i % len(colors)])
        draw = ImageDraw.Draw(img)

        # Add text
        text = texts[i % len(texts)]
        # Try to center text
        bbox = draw.textbbox((0, 0), text)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (1920 - text_width) // 2
        y = (1080 - text_height) // 2
        draw.text((x, y), text, fill=(255, 245, 220))

        image_path = output_dir / f"image_{i+1}.png"
        img.save(image_path)
        images.append(str(image_path))
        print(f"  ✅ Placeholder image {i+1} created")

    return images

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
    print("🎬 Creating video with FFmpeg...")

    # Get audio duration
    duration = get_audio_duration(audio_path)
    print(f"  Audio duration: {duration:.2f} seconds")

    # Calculate duration per image
    num_images = len(images)
    image_duration = duration / num_images
    print(f"  Each image will show for: {image_duration:.2f} seconds")

    # Create a file list for FFmpeg
    filelist_path = OUTPUT_DIR / "filelist.txt"
    with open(filelist_path, 'w') as f:
        for img in images:
            f.write(f"file '{img}'\n")
            f.write(f"duration {image_duration}\n")
        # Add last image again (FFmpeg quirk)
        f.write(f"file '{images[-1]}'\n")

    # FFmpeg command to create video
    cmd = [
        'ffmpeg', '-y',
        '-f', 'concat',
        '-safe', '0',
        '-i', str(filelist_path),
        '-i', str(audio_path),
        '-c:v', 'libx264',
        '-pix_fmt', 'yuv420p',
        '-c:a', 'aac',
        '-shortest',
        '-movflags', '+faststart',
        str(output_path)
    ]

    print("  Running FFmpeg...")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        print(f"✅ Video created successfully: {output_path}")
        return True
    else:
        print(f"❌ FFmpeg Error: {result.stderr}")
        return False

def main():
    print("=" * 50)
    print("🎬 VIDEO GENERATOR - 1920s America Theme")
    print("=" * 50)

    # Paths
    audio_path = OUTPUT_DIR / "narration.mp3"
    video_path = OUTPUT_DIR / "final_video.mp4"

    # Step 1: Generate voice (skip if already exists)
    print("\n📌 Step 1: Voice Generation")
    if audio_path.exists():
        print(f"✅ Audio already exists: {audio_path}")
        voice_success = True
    else:
        voice_success = generate_voice(SCRIPT, audio_path)

    if not voice_success:
        print("❌ Failed to generate voice. Exiting.")
        return

    # Step 2: Generate images with Ideogram
    print("\n📌 Step 2: Image Generation (Ideogram)")
    images = generate_images_ideogram(IMAGE_PROMPTS, OUTPUT_DIR)

    # If Ideogram fails, use placeholder images
    if len(images) < 3:
        print("\n⚠️ Ideogram API issue. Creating placeholder images instead...")
        images = generate_placeholder_images(6, OUTPUT_DIR)

    # Step 3: Create video
    print("\n📌 Step 3: Video Creation")
    video_success = create_video(images, audio_path, video_path)

    if video_success:
        print("\n" + "=" * 50)
        print("🎉 VIDEO GENERATION COMPLETE!")
        print(f"📁 Output: {video_path}")
        print("=" * 50)
    else:
        print("\n❌ Video generation failed.")

if __name__ == "__main__":
    main()
