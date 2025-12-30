#!/usr/bin/env python3
"""
Generate infographic images from YAML configuration.
"""

import argparse
import os
import sys
from pathlib import Path

import yaml
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

def load_yaml(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def generate_image(client: genai.Client, prompt: str, output_path: str, aspect_ratio: str = "16:9", image_size: str = "2K"):
    print(f"🎨 Generating image for: {output_path}...")
    try:
        response = client.models.generate_content(
            model="gemini-3-pro-image-preview",
            contents=[prompt],
            config=types.GenerateContentConfig(
                response_modalities=["TEXT", "IMAGE"],
                image_config=types.ImageConfig(
                    aspect_ratio=aspect_ratio,
                ),
            ),
        )

        for part in response.parts:
            if hasattr(part, "inline_data") and part.inline_data:
                 pass # wait, 3-preview might return differently? infographic.py uses part.as_image().
            
            if image := part.as_image():
                image.save(output_path)
                print(f"✅ Saved to {output_path}")
                return True
        
        print(f"⚠️ No image generated for {output_path}")
        return False

    except Exception as e:
        print(f"❌ Error generating {output_path}: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Generate images from YAML")
    parser.add_argument("yaml_file", help="Path to YAML file")
    args = parser.parse_args()

    config = load_yaml(args.yaml_file)
    
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY or GOOGLE_API_KEY not found in environment.")
        print("Please set it via: export GEMINI_API_KEY='your_key'")
        return

    client = genai.Client(api_key=api_key)

    output_base = Path("output/images")
    output_base.mkdir(parents=True, exist_ok=True)

    images = config.get("images", [])
    total = len(images)
    success = 0

    print(f"Found {total} images to generate.")

    for img_conf in images:
        img_id = img_conf.get("id")
        prompt = img_conf.get("prompt")
        aspect = img_conf.get("aspect_ratio", "16:9")
        size = img_conf.get("image_size", "2K") # Note: Yaml has '2K', API might expect something else or string is fine? infographic.py uses string "2K".

        if not img_id or not prompt:
            print(f"Skipping invalid config: {img_conf}")
            continue

        output_path = output_base / f"{img_id}.png"
        
        # Check if exists? Maybe overwrite is better.
        
        if generate_image(client, prompt, str(output_path), aspect, size):
            success += 1

    print(f"\nFinished. Success: {success}/{total}")

if __name__ == "__main__":
    main()
