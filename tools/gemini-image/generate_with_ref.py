#!/usr/bin/env python3
"""
参照画像スタイルを使ってインフォグラフィックを生成

Usage:
    python generate_with_ref.py --ref /path/to/reference.png
"""

import os
import sys
import base64
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

output_dir = Path("/Users/shunsukehayashi/dev/seminar/output/images_v2")
output_dir.mkdir(parents=True, exist_ok=True)

# Style description based on reference image
STYLE_REFERENCE = """
Match this exact visual style:
- Cream/beige paper texture background (NOT pure white)
- Simple stick figures with round heads and minimal features
- Hand-drawn machines with visible gears and mechanical details
- Color palette: black outlines, soft yellow highlights, light blue accents
- Japanese handwritten text labels (neat but hand-drawn feel)
- Clean, minimal composition with clear sections
- Warm, friendly, approachable tone
- Soft colored pencil/marker texture
- Similar layout: split comparison with clear A/B sections
"""

PROMPTS = [
    {
        "id": "01_ai_agent_overview",
        "title": "AIエージェント全体像",
        "prompt": f"""Create a hand-drawn infographic in the EXACT same style as the reference image.

{STYLE_REFERENCE}

Content to illustrate:
Title: 「AIエージェントの正体」

Left side (A): 脳みそ（スキル）
- Stick figure with a brain/lightbulb above head
- Document/memo labeled "スキル.md"
- Speech bubble: "手順書で考える"
- Label: "プロンプト（柔軟に対応）"

Right side (B): 手足（MCPツール）
- Same stick figure next to a machine with gears
- Machine labeled "MCPサーバー"
- Speech bubble: "ツールで実行"
- Label: "プログラム（確実に動作）"

Bottom: Combined equation
- 脳みそ + 手足 = AIエージェント

Keep the same warm cream background, stick figure style, and hand-drawn aesthetic.
"""
    },
    {
        "id": "02_mcp_three_elements",
        "title": "MCPの3要素",
        "prompt": f"""Create a hand-drawn infographic in the EXACT same style as the reference image.

{STYLE_REFERENCE}

Content to illustrate:
Title: 「MCPの3つの要素」

Show three columns/sections:

Column 1 - リソース:
- Document/folder icon
- Label: "データ提供"
- Stick figure pointing at data

Column 2 - プロンプト:
- Chat bubble icon
- Label: "テンプレート提供"
- Stick figure with thought bubble

Column 3 - ツール (highlighted with yellow):
- Wrench/gear icon like the machine in reference
- Label: "実行機能 ※重要！"
- Stick figure using the tool

Bottom: USB-C cable metaphor
- Simple cable drawing
- Label: "MCP = AIのUSB-C規格"

Keep the same warm cream background and hand-drawn aesthetic.
"""
    },
    {
        "id": "03_skill_vs_tool_v2",
        "title": "スキル vs MCPツール（参照スタイル）",
        "prompt": f"""Create a hand-drawn infographic in the EXACT same style as the reference image.

{STYLE_REFERENCE}

Content to illustrate:
Title: 「スキルとMCPツールの違い」

Left side (A): スキル = 脳みそ
- Stick figure reading a book/manual
- Book labeled "業務マニュアル"
- Lightbulb above head
- Speech bubble: "こうやって仕事するんだよ"
- Note: "プロンプト = 柔軟に判断"

Right side (B): MCPツール = 手足
- Same style stick figure using a machine with gears
- Machine similar to reference image style
- Button labeled "実行ボタン"
- Speech bubble: "確実に動作"
- Note: "プログラム = ブレない処理"

Bottom center:
- Both elements combining
- Label: "組み合わせ = 仕事ができる社員"

Keep the exact same cream background, stick figure style, and machine aesthetic from reference.
"""
    },
    {
        "id": "04_workflow_comparison",
        "title": "従来型 vs エージェント型",
        "prompt": f"""Create a hand-drawn infographic in the EXACT same style as the reference image.

{STYLE_REFERENCE}

Content to illustrate:
Title: 「ワークフローの進化」

Top section (A): 従来型
- Complex flowchart with many arrows and diamonds
- Stressed stick figure managing it
- Red X mark
- Labels: "IF文", "分岐", "全部決める必要あり"
- Note: "N8N/Dify/Zapier"

Bottom section (B): エージェント型
- Simple flow: スタート → AI（ロボット）→ ゴール
- Happy stick figure just setting goal
- Green checkmark
- Labels: "ゴールだけ伝える", "道はAIが選ぶ"
- Note: "ゴールシーク"

Keep the same warm cream background and hand-drawn aesthetic with clear A/B comparison.
"""
    },
    {
        "id": "05_roadmap",
        "title": "エージェントマスターへの道",
        "prompt": f"""Create a hand-drawn infographic in the EXACT same style as the reference image.

{STYLE_REFERENCE}

Content to illustrate:
Title: 「AIエージェントマスターへの道」

Show a path/journey from left to right:

Start (left):
- Stick figure at "今ここ" sign
- Looking ahead

Path with 4 milestones (stepping stones):
1. "MCPを理解する"
2. "スキルを作る"
3. "ツールを作る"
4. "組み合わせる"

Goal (right):
- Triumphant stick figure with raised arms
- Robot/machine partner next to them
- Stars around
- Banner: "AIエージェント完成！"
- Note: "2025年はエージェント元年"

Keep the same warm cream background and encouraging, friendly tone.
"""
    }
]


def generate_with_reference(prompt_data: Dict, ref_image_path: Optional[str] = None) -> Optional[str]:
    """Generate image with optional style reference"""
    print(f"\n🎨 Generating: {prompt_data['title']}...")
    
    try:
        contents = []
        
        # Add reference image if provided
        if ref_image_path and Path(ref_image_path).exists():
            ref_image = Image.open(ref_image_path)
            contents.append("Use this image as a style reference. Match the exact visual style, colors, and hand-drawn aesthetic:")
            contents.append(ref_image)
            contents.append("\nNow create a new infographic with the following content:\n")
        
        contents.append(prompt_data["prompt"])
        
        response = client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=contents,
            config=types.GenerateContentConfig(
                response_modalities=["TEXT", "IMAGE"],
            ),
        )
        
        output_path = output_dir / f"{prompt_data['id']}.png"
        
        for part in response.parts:
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
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--ref", help="Reference image path for style")
    args = parser.parse_args()
    
    ref_path = args.ref
    
    print("=" * 60)
    print("📊 参照スタイルでインフォグラフィック生成")
    print("=" * 60)
    if ref_path:
        print(f"参照画像: {ref_path}")
    print(f"出力先: {output_dir}")
    print(f"生成数: {len(PROMPTS)}枚")
    
    results = []
    for prompt_data in PROMPTS:
        result = generate_with_reference(prompt_data, ref_path)
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
