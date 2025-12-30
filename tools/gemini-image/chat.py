#!/usr/bin/env python3
"""
Gemini 3 Pro Image Preview - マルチターン画像チャット

Usage:
    python chat.py [options]

インタラクティブなチャットセッションで画像を生成・編集
"""

import argparse
import os
import readline
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types
from PIL import Image

load_dotenv()


class ImageChat:
    def __init__(
        self,
        model: str = "pro",
        aspect_ratio: str = "1:1",
        image_size: str = "2K",
        use_search: bool = False,
    ):
        self.client = genai.Client()
        self.model = model
        self.aspect_ratio = aspect_ratio
        self.image_size = image_size
        self.use_search = use_search
        self.image_counter = 0

        model_id = (
            "gemini-3-pro-image-preview"
            if model == "pro"
            else "gemini-2.5-flash-image"
        )

        config_params = {
            "response_modalities": ["TEXT", "IMAGE"],
        }

        if model == "pro":
            config_params["image_config"] = types.ImageConfig(
                aspect_ratio=aspect_ratio,
                image_size=image_size,
            )
            if use_search:
                config_params["tools"] = [{"google_search": {}}]

        self.chat = self.client.chats.create(
            model=model_id,
            config=types.GenerateContentConfig(**config_params),
        )

    def send(self, message: str, image_path: str | None = None) -> dict:
        """メッセージを送信"""
        contents = [message]
        if image_path:
            contents.append(Image.open(image_path))

        response = self.chat.send_message(contents)

        result = {"text": None, "image_path": None}

        for part in response.parts:
            if not (hasattr(part, "thought") and part.thought):
                if part.text:
                    result["text"] = part.text
                elif image := part.as_image():
                    self.image_counter += 1
                    output_path = f"chat_output_{self.image_counter:03d}.png"
                    image.save(output_path)
                    result["image_path"] = output_path

        return result

    def update_config(self, aspect_ratio: str = None, image_size: str = None):
        """設定を更新"""
        if aspect_ratio:
            self.aspect_ratio = aspect_ratio
        if image_size:
            self.image_size = image_size


def main():
    parser = argparse.ArgumentParser(description="Gemini Image Chat")
    parser.add_argument("-m", "--model", default="pro", choices=["flash", "pro"])
    parser.add_argument("-a", "--aspect", default="1:1", help="アスペクト比")
    parser.add_argument("-s", "--size", default="2K", choices=["1K", "2K", "4K"])
    parser.add_argument("--search", action="store_true", help="Google検索有効化")

    args = parser.parse_args()

    print("🎨 Gemini Image Chat")
    print(f"   Model: {args.model}, Aspect: {args.aspect}, Size: {args.size}")
    print("\nCommands:")
    print("  /quit or /exit  - 終了")
    print("  /aspect <ratio> - アスペクト比変更 (e.g., /aspect 16:9)")
    print("  /size <size>    - 解像度変更 (e.g., /size 4K)")
    print("  /image <path>   - 画像を添付して送信")
    print("-" * 50)

    chat = ImageChat(
        model=args.model,
        aspect_ratio=args.aspect,
        image_size=args.size,
        use_search=args.search,
    )

    while True:
        try:
            user_input = input("\n📝 You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n👋 Bye!")
            break

        if not user_input:
            continue

        if user_input.lower() in ["/quit", "/exit"]:
            print("👋 Bye!")
            break

        if user_input.startswith("/aspect "):
            new_aspect = user_input.split(" ", 1)[1]
            chat.update_config(aspect_ratio=new_aspect)
            print(f"✅ Aspect ratio set to: {new_aspect}")
            continue

        if user_input.startswith("/size "):
            new_size = user_input.split(" ", 1)[1].upper()
            if new_size in ["1K", "2K", "4K"]:
                chat.update_config(image_size=new_size)
                print(f"✅ Image size set to: {new_size}")
            else:
                print("❌ Invalid size. Use 1K, 2K, or 4K")
            continue

        image_path = None
        if user_input.startswith("/image "):
            parts = user_input.split(" ", 2)
            if len(parts) >= 3:
                image_path = parts[1]
                user_input = parts[2]
            else:
                print("❌ Usage: /image <path> <message>")
                continue

        print("🔄 Generating...")
        result = chat.send(user_input, image_path)

        if result["text"]:
            print(f"\n🤖 Gemini: {result['text']}")

        if result["image_path"]:
            print(f"🖼️  Image saved: {result['image_path']}")


if __name__ == "__main__":
    main()
