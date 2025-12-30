#!/usr/bin/env python3
"""
Gemini 3 Pro Image Preview - 手書き風インフォグラフィック生成

Usage:
    python infographic.py "概念" [options]
    python infographic.py --yaml config.yaml

Options:
    --output, -o     出力ファイルパス (default: infographic.png)
    --aspect, -a     アスペクト比 (default: 16:9)
    --size, -s       解像度 (default: 2K)
    --yaml, -y       YAML設定ファイルパス
    --style          スタイル preset (notebook/whiteboard/minimal)
"""

import argparse
import os
from pathlib import Path

import yaml
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

# スタイルプリセット
STYLE_PRESETS = {
    "notebook": {
        "aesthetic": "Hand-drawn sketch on notebook paper",
        "texture": "Pencil, pen, and highlighter on lined paper",
        "vibe": "Friendly, approachable, like a student's notebook",
        "imperfection": "Slightly messy, authentic hand-drawn feel",
    },
    "whiteboard": {
        "aesthetic": "Whiteboard marker drawing",
        "texture": "Dry-erase markers on white surface",
        "vibe": "Clean, professional, like a meeting whiteboard",
        "imperfection": "Smooth lines with occasional marker streaks",
    },
    "minimal": {
        "aesthetic": "Minimalist infographic",
        "texture": "Clean digital illustration with hand-drawn elements",
        "vibe": "Modern, simple, easy to understand",
        "imperfection": "Subtle hand-drawn touches on clean design",
    },
}

COLOR_PALETTE = {
    "background": "white or off-white paper",
    "text": "black or dark charcoal",
    "emphasis": "yellow or orange highlights",
    "structure": "blue or green for organization",
    "warning": "red for important notes",
}


def build_infographic_prompt(
    concept: str,
    labels: list[dict] | None = None,
    annotation: str | None = None,
    style: str = "notebook",
    custom_elements: str | None = None,
) -> str:
    """インフォグラフィック用プロンプトを構築"""
    preset = STYLE_PRESETS.get(style, STYLE_PRESETS["notebook"])

    prompt = f"""Create a hand-drawn infographic explaining: {concept}

Style:
- {preset['aesthetic']}
- {preset['texture']}
- {preset['vibe']}
- {preset['imperfection']}

Color Palette:
- Background: {COLOR_PALETTE['background']}
- Text/Outlines: {COLOR_PALETTE['text']}
- Emphasis: {COLOR_PALETTE['emphasis']}
- Structure: {COLOR_PALETTE['structure']}
- Warnings: {COLOR_PALETTE['warning']}

Visual Elements:
- Simple stick figures with expressive faces for any characters
- Hand-drawn arrows showing flow and relationships
- Hand-drawn boxes, circles, and speech bubbles for grouping
- Handwritten Japanese text labels (must be readable)
"""

    if labels:
        prompt += "\nJapanese Labels:\n"
        for label in labels:
            prompt += f"- \"{label['text']}\" pointing to {label['target']}\n"

    if annotation:
        prompt += f"\nKey Takeaway (handwritten Japanese annotation):\n\"{annotation}\"\n"

    if custom_elements:
        prompt += f"\nAdditional Elements:\n{custom_elements}\n"

    prompt += """
Layout Guidelines:
- Clear visual hierarchy with main concept prominent
- Logical flow from left to right or top to bottom
- Adequate whitespace for readability
- All text must be in Japanese
"""

    return prompt


def generate_infographic(
    concept: str,
    output_path: str = "infographic.png",
    aspect_ratio: str = "16:9",
    image_size: str = "2K",
    style: str = "notebook",
    labels: list[dict] | None = None,
    annotation: str | None = None,
    custom_elements: str | None = None,
) -> dict:
    """インフォグラフィックを生成"""
    client = genai.Client()

    prompt = build_infographic_prompt(
        concept=concept,
        labels=labels,
        annotation=annotation,
        style=style,
        custom_elements=custom_elements,
    )

    response = client.models.generate_content(
        model="gemini-3-pro-image-preview",
        contents=[prompt],
        config=types.GenerateContentConfig(
            response_modalities=["TEXT", "IMAGE"],
            image_config=types.ImageConfig(
                aspect_ratio=aspect_ratio,
                image_size=image_size,
            ),
        ),
    )

    result = {"text": None, "image_path": None, "prompt": prompt}

    for part in response.parts:
        if not (hasattr(part, "thought") and part.thought):
            if part.text:
                result["text"] = part.text
            elif image := part.as_image():
                image.save(output_path)
                result["image_path"] = output_path

    return result


def load_yaml_config(yaml_path: str) -> dict:
    """YAML設定ファイルを読み込み"""
    with open(yaml_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def main():
    parser = argparse.ArgumentParser(description="Gemini Hand-drawn Infographic Generator")
    parser.add_argument("concept", nargs="?", help="説明する概念")
    parser.add_argument("-o", "--output", default="infographic.png", help="出力ファイルパス")
    parser.add_argument("-a", "--aspect", default="16:9", help="アスペクト比")
    parser.add_argument("-s", "--size", default="2K", choices=["1K", "2K", "4K"], help="解像度")
    parser.add_argument("--style", default="notebook", choices=["notebook", "whiteboard", "minimal"])
    parser.add_argument("-y", "--yaml", help="YAML設定ファイルパス")
    parser.add_argument("--annotation", help="要約アノテーション（日本語）")
    parser.add_argument("--show-prompt", action="store_true", help="生成プロンプトを表示")

    args = parser.parse_args()

    # YAML設定ファイルからの読み込み
    if args.yaml:
        config = load_yaml_config(args.yaml)
        concept = config.get("concept", args.concept)
        labels = config.get("labels")
        annotation = config.get("annotation", args.annotation)
        custom_elements = config.get("custom_elements")
        style = config.get("style", args.style)
        aspect_ratio = config.get("aspect_ratio", args.aspect)
        image_size = config.get("image_size", args.size)
        output_path = config.get("output", args.output)
    else:
        if not args.concept:
            parser.error("concept is required unless using --yaml")
        concept = args.concept
        labels = None
        annotation = args.annotation
        custom_elements = None
        style = args.style
        aspect_ratio = args.aspect
        image_size = args.size
        output_path = args.output

    print(f"📊 Generating hand-drawn infographic...")
    print(f"   Concept: {concept}")
    print(f"   Style: {style}, Aspect: {aspect_ratio}, Size: {image_size}")

    result = generate_infographic(
        concept=concept,
        output_path=output_path,
        aspect_ratio=aspect_ratio,
        image_size=image_size,
        style=style,
        labels=labels,
        annotation=annotation,
        custom_elements=custom_elements,
    )

    if args.show_prompt:
        print(f"\n📝 Generated Prompt:\n{result['prompt']}")

    if result["text"]:
        print(f"\n💬 Response:\n{result['text']}")

    if result["image_path"]:
        print(f"\n✅ Infographic saved to: {result['image_path']}")


if __name__ == "__main__":
    main()
