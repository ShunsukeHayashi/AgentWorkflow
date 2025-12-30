#!/usr/bin/env python3
"""
Gemini 3 Pro Image Preview - 画像編集ツール

Usage:
    python edit.py "編集指示" --input image.png [options]

Options:
    --input, -i      入力画像パス (required)
    --output, -o     出力ファイルパス (default: edited.png)
    --aspect, -a     アスペクト比 (default: 入力画像に合わせる)
    --size, -s       解像度 1K/2K/4K (default: 2K)
    --model, -m      モデル flash/pro (default: pro)
"""

import argparse
import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types
from PIL import Image

load_dotenv()


def edit_image(
    prompt: str,
    input_path: str,
    output_path: str = "edited.png",
    aspect_ratio: str | None = None,
    image_size: str = "2K",
    model: str = "pro",
    additional_images: list[str] | None = None,
) -> dict:
    """
    既存画像を編集

    Args:
        prompt: 編集指示プロンプト
        input_path: 入力画像パス
        output_path: 出力ファイルパス
        aspect_ratio: アスペクト比 (None=入力画像に合わせる)
        image_size: 解像度 (1K, 2K, 4K)
        model: モデル選択 (flash or pro)
        additional_images: 追加の参照画像パスリスト

    Returns:
        dict: 編集結果
    """
    client = genai.Client()

    model_id = (
        "gemini-3-pro-image-preview"
        if model == "pro"
        else "gemini-2.5-flash-image"
    )

    # 入力画像を読み込み
    input_image = Image.open(input_path)

    # コンテンツ構築
    contents = [prompt, input_image]

    # 追加の参照画像（Proモデルは最大14枚）
    if additional_images:
        for img_path in additional_images:
            contents.append(Image.open(img_path))

    config_params = {
        "response_modalities": ["TEXT", "IMAGE"],
    }

    if aspect_ratio:
        if model == "pro":
            config_params["image_config"] = types.ImageConfig(
                aspect_ratio=aspect_ratio,
                image_size=image_size,
            )
        else:
            config_params["image_config"] = types.ImageConfig(
                aspect_ratio=aspect_ratio,
            )

    response = client.models.generate_content(
        model=model_id,
        contents=contents,
        config=types.GenerateContentConfig(**config_params),
    )

    result = {"text": None, "image_path": None}

    for part in response.parts:
        if not (hasattr(part, "thought") and part.thought):
            if part.text:
                result["text"] = part.text
            elif image := part.as_image():
                image.save(output_path)
                result["image_path"] = output_path

    return result


def main():
    parser = argparse.ArgumentParser(description="Gemini 3 Pro Image Editing")
    parser.add_argument("prompt", help="編集指示プロンプト")
    parser.add_argument("-i", "--input", required=True, help="入力画像パス")
    parser.add_argument("-o", "--output", default="edited.png", help="出力ファイルパス")
    parser.add_argument("-a", "--aspect", help="アスペクト比")
    parser.add_argument("-s", "--size", default="2K", choices=["1K", "2K", "4K"], help="解像度")
    parser.add_argument("-m", "--model", default="pro", choices=["flash", "pro"], help="モデル")
    parser.add_argument("--refs", nargs="*", help="追加の参照画像パス")

    args = parser.parse_args()

    print(f"✏️ Editing image with {args.model} model...")
    print(f"   Input: {args.input}")
    print(f"   Prompt: {args.prompt[:50]}...")

    result = edit_image(
        prompt=args.prompt,
        input_path=args.input,
        output_path=args.output,
        aspect_ratio=args.aspect,
        image_size=args.size,
        model=args.model,
        additional_images=args.refs,
    )

    if result["text"]:
        print(f"\n📝 Text response:\n{result['text']}")

    if result["image_path"]:
        print(f"\n✅ Edited image saved to: {result['image_path']}")


if __name__ == "__main__":
    main()
