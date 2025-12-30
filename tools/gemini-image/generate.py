#!/usr/bin/env python3
"""
Gemini 3 Pro Image Preview - 画像生成ツール

Usage:
    python generate.py "プロンプト" [options]

Options:
    --output, -o     出力ファイルパス (default: output.png)
    --aspect, -a     アスペクト比 (default: 1:1)
    --size, -s       解像度 1K/2K/4K (default: 2K)
    --model, -m      モデル flash/pro (default: pro)
    --search         Google検索グラウンディング有効化
"""

import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()


def generate_image(
    prompt: str,
    output_path: str = "output.png",
    aspect_ratio: str = "1:1",
    image_size: str = "2K",
    model: str = "pro",
    use_search: bool = False,
) -> dict:
    """
    Gemini APIで画像を生成

    Args:
        prompt: 画像生成プロンプト
        output_path: 出力ファイルパス
        aspect_ratio: アスペクト比 (1:1, 16:9, 9:16, etc.)
        image_size: 解像度 (1K, 2K, 4K) - Proモデルのみ
        model: モデル選択 (flash or pro)
        use_search: Google検索グラウンディング使用

    Returns:
        dict: 生成結果 (text, image_path, thinking)
    """
    client = genai.Client()

    model_id = (
        "gemini-3-pro-image-preview"
        if model == "pro"
        else "gemini-2.5-flash-image"
    )

    config_params = {
        "response_modalities": ["TEXT", "IMAGE"],
        "image_config": types.ImageConfig(aspect_ratio=aspect_ratio),
    }

    # Proモデルのみimage_sizeをサポート
    if model == "pro":
        config_params["image_config"] = types.ImageConfig(
            aspect_ratio=aspect_ratio,
            image_size=image_size,
        )

    # Google検索グラウンディング (Proモデルのみ)
    if use_search and model == "pro":
        config_params["tools"] = [{"google_search": {}}]

    response = client.models.generate_content(
        model=model_id,
        contents=[prompt],
        config=types.GenerateContentConfig(**config_params),
    )

    result = {"text": None, "image_path": None, "thinking": []}

    for part in response.parts:
        if hasattr(part, "thought") and part.thought:
            # 思考プロセス（中間画像）
            if part.text:
                result["thinking"].append({"type": "text", "content": part.text})
            elif image := part.as_image():
                thinking_path = f"thinking_{len(result['thinking'])}.png"
                image.save(thinking_path)
                result["thinking"].append({"type": "image", "path": thinking_path})
        else:
            # 最終出力
            if part.text:
                result["text"] = part.text
            elif image := part.as_image():
                image.save(output_path)
                result["image_path"] = output_path

    return result


def main():
    parser = argparse.ArgumentParser(description="Gemini 3 Pro Image Generation")
    parser.add_argument("prompt", help="画像生成プロンプト")
    parser.add_argument("-o", "--output", default="output.png", help="出力ファイルパス")
    parser.add_argument("-a", "--aspect", default="1:1", help="アスペクト比")
    parser.add_argument("-s", "--size", default="2K", choices=["1K", "2K", "4K"], help="解像度")
    parser.add_argument("-m", "--model", default="pro", choices=["flash", "pro"], help="モデル")
    parser.add_argument("--search", action="store_true", help="Google検索グラウンディング")

    args = parser.parse_args()

    print(f"🎨 Generating image with {args.model} model...")
    print(f"   Prompt: {args.prompt[:50]}...")
    print(f"   Aspect: {args.aspect}, Size: {args.size}")

    result = generate_image(
        prompt=args.prompt,
        output_path=args.output,
        aspect_ratio=args.aspect,
        image_size=args.size,
        model=args.model,
        use_search=args.search,
    )

    if result["text"]:
        print(f"\n📝 Text response:\n{result['text']}")

    if result["image_path"]:
        print(f"\n✅ Image saved to: {result['image_path']}")

    if result["thinking"]:
        print(f"\n🧠 Thinking process: {len(result['thinking'])} steps")


if __name__ == "__main__":
    main()
