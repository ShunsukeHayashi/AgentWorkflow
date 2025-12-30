#!/usr/bin/env python3
"""
Nano Banana Pro (gemini-3-pro-image-preview) でインフォグラフィック生成
"""

import os
import sys
from pathlib import Path
from typing import Optional, Dict

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
if not api_key:
    print("❌ GEMINI_API_KEY が設定されていません")
    sys.exit(1)

from google import genai
from google.genai import types
from PIL import Image

client = genai.Client(api_key=api_key)

output_dir = Path("/Users/shunsukehayashi/dev/seminar/output/images_pro")
output_dir.mkdir(parents=True, exist_ok=True)

# Style based on reference image
STYLE = """
Visual Style Requirements (MUST FOLLOW EXACTLY):
- Cream/beige textured paper background (warm off-white, NOT pure white)
- Simple stick figures with round heads, dot eyes, simple smile
- Hand-drawn machines with visible gears, knobs, and mechanical details
- Color palette: black outlines, soft yellow highlights, light blue accents
- Japanese handwritten text labels (neat but authentic hand-drawn feel)
- Soft colored pencil and marker texture throughout
- Clean, minimal composition with clear visual hierarchy
- Warm, friendly, approachable educational tone
- Split A/B comparison layout where applicable
"""

PROMPTS = [
    {
        "id": "01_ai_agent",
        "title": "AIエージェント全体像",
        "prompt": f"""Create a hand-drawn educational infographic.

{STYLE}

Title at top: 「AIエージェントの正体」

Layout: Split into two sections (A and B) side by side

Section A (Left) - 脳みそ（スキル）:
- Cute stick figure reading a document
- Document labeled "SKILL.md（手順書メモ）"
- Lightbulb icon above head showing "thinking"
- Speech bubble: "手順書で考える"
- Small label below: "プロンプト = 柔軟に対応"

Section B (Right) - 手足（MCPツール）:
- Same style stick figure standing next to a machine
- Machine has gears, buttons, and mechanical details
- Machine labeled "MCPサーバー（道具・プログラム）"
- Speech bubble from machine: "確実に実行"
- Small label below: "プログラム = ブレない処理"

Bottom center:
- Simple equation: 脳みそ + 手足 = AIエージェント
- Small robot icon combining both elements
"""
    },
    {
        "id": "02_mcp_elements",
        "title": "MCPの3要素",
        "prompt": f"""Create a hand-drawn educational infographic.

{STYLE}

Title at top: 「MCPの3つの要素」

Layout: Three columns with icons and labels

Column 1 - リソース:
- Folder/document icon (hand-drawn)
- Label: "リソース"
- Subtitle: "データを提供"
- Small stick figure pointing at documents

Column 2 - プロンプト:
- Chat bubble icon (hand-drawn)
- Label: "プロンプト"
- Subtitle: "テンプレート提供"
- Small stick figure with thought bubble

Column 3 - ツール (HIGHLIGHTED with yellow):
- Wrench and gear icon (hand-drawn, detailed like reference)
- Label: "ツール" with yellow highlight
- Subtitle: "実行機能 ※これが重要！"
- Small stick figure operating machine

Bottom:
- USB-C cable drawing
- Label: "MCP = AIのUSB-C規格（統一された接続方法）"
"""
    },
    {
        "id": "03_skill_vs_mcp",
        "title": "スキル vs MCPツール",
        "prompt": f"""Create a hand-drawn educational infographic.

{STYLE}

Title at top: 「Hello World」に見る Skill と MCP の違い

Layout: Split into A and B sections (like reference image)

Section A (Left) - Skill（スキル）での Hello World:
- Stick figure with lightbulb, reading a memo
- Memo/note paper labeled "SKILL.md（手順書メモ）"
- Text on memo: "挨拶を求められたら『Hello World』と返す"
- Speech bubble from figure: "Hello World（自分で生成）"
- Label at bottom: "AI（新人バイト）"

Section B (Right) - MCPサーバー での Hello World:
- Stick figure standing next to machine with gears
- Machine has a button labeled "挨拶機能ボタン"
- Speech bubble from machine: "Hello World（道具が実行）"
- Labels: "AI（新人バイト）" and "MCPサーバー（道具・プログラム）"

The machine should have detailed gears and mechanical parts like the reference image.
"""
    },
    {
        "id": "04_workflow",
        "title": "従来型 vs エージェント型",
        "prompt": f"""Create a hand-drawn educational infographic.

{STYLE}

Title at top: 「ワークフローの進化」

Layout: Top/Bottom comparison (Before/After)

Top Section - 従来型ワークフロー:
- Complex flowchart with many boxes, arrows, diamond decision points
- Stressed stick figure trying to manage all the connections
- Red X mark
- Labels scattered: "IF文", "分岐", "全部決める", "N8N/Dify"
- Caption: "1から100まで全部自分で設計..."

Bottom Section - エージェント型ワークフロー:
- Simple clean flow: スタート → AIロボット → ゴール
- Happy relaxed stick figure just pointing at goal
- Green checkmark
- Robot/machine choosing its own path (multiple dotted lines)
- Labels: "ゴールだけ伝える！", "道はAIが選ぶ"
- Caption: "ゴールシーク = 目標だけ指示"
"""
    },
    {
        "id": "05_roadmap",
        "title": "エージェントマスターへの道",
        "prompt": f"""Create a hand-drawn educational infographic.

{STYLE}

Title at top: 「AIエージェントマスターへの道」

Layout: Journey/path from left to right going upward

Starting point (bottom left):
- Stick figure with "今ここ" (You are here) sign
- Looking forward with curiosity

Path with 4 stepping stones/milestones going up-right:
- Stone 1: "Step 1: MCPを知る" (with book icon)
- Stone 2: "Step 2: スキルを作る" (with document icon)
- Stone 3: "Step 3: ツールを作る" (with gear icon)
- Stone 4: "Step 4: 組み合わせる" (with puzzle icon)

Goal (top right):
- Triumphant stick figure with arms raised
- Friendly robot partner next to them
- Stars and sparkles around
- Banner: "AIエージェント完成！"
- Ribbon/badge: "2025年はエージェント元年"

Make it feel like an encouraging, achievable journey.
"""
    }
]


def generate_image(prompt_data: Dict) -> Optional[str]:
    """Generate image with Nano Banana Pro"""
    print(f"\n🎨 Generating: {prompt_data['title']}...")
    
    try:
        response = client.models.generate_content(
            model="gemini-3-pro-image-preview",  # Nano Banana Pro
            contents=[prompt_data["prompt"]],
            config=types.GenerateContentConfig(
                response_modalities=["TEXT", "IMAGE"],
                image_config=types.ImageConfig(
                    aspect_ratio="16:9"
                ),
            ),
        )
        
        output_path = output_dir / f"{prompt_data['id']}.png"
        
        for part in response.parts:
            # Skip thinking parts
            if hasattr(part, "thought") and part.thought:
                continue
            if hasattr(part, "text") and part.text:
                print(f"   📝 {part.text[:80]}...")
            if hasattr(part, "inline_data") and part.inline_data:
                image = part.as_image()
                image.save(str(output_path))
                print(f"   ✅ Saved: {output_path}")
                return str(output_path)
        
        print(f"   ⚠️ No image generated")
        return None
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None


def main():
    print("=" * 60)
    print("🍌 Nano Banana Pro インフォグラフィック生成")
    print("   Model: gemini-3-pro-image-preview")
    print("   Resolution: 2K, Aspect: 16:9")
    print("=" * 60)
    print(f"出力先: {output_dir}")
    print(f"生成数: {len(PROMPTS)}枚")
    
    results = []
    for prompt_data in PROMPTS:
        result = generate_image(prompt_data)
        results.append({
            "id": prompt_data["id"],
            "title": prompt_data["title"],
            "path": result,
            "success": result is not None
        })
    
    print("\n" + "=" * 60)
    print("📋 生成結果")
    print("=" * 60)
    
    success = sum(1 for r in results if r["success"])
    print(f"成功: {success}/{len(results)}")
    
    for r in results:
        status = "✅" if r["success"] else "❌"
        print(f"  {status} {r['title']}")
    
    print("\n完了！")


if __name__ == "__main__":
    main()
