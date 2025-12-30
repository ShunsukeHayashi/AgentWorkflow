#!/usr/bin/env python3
"""
全インフォグラフィック画像を一括生成

Usage:
    python generate_all.py
"""

import os
import sys
from pathlib import Path
from typing import Optional, Dict, List

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Check for API key
api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
if not api_key:
    print("❌ GEMINI_API_KEY または GOOGLE_API_KEY が設定されていません")
    print("   export GEMINI_API_KEY=your_key")
    sys.exit(1)

from google import genai
from google.genai import types

client = genai.Client(api_key=api_key)

# Output directory
output_dir = Path("/Users/shunsukehayashi/dev/seminar/output/images")
output_dir.mkdir(parents=True, exist_ok=True)

# 5 infographic prompts
PROMPTS = [
    {
        "id": "01_ai_agent_overview",
        "title": "AIエージェント全体像",
        "prompt": """Create a hand-drawn infographic explaining AI Agent architecture.

Style:
- Graphic recording / whiteboard art style
- Marker pens and colored pencils texture on paper
- Friendly, approachable, like a student's notebook
- Slightly imperfect lines (not polished digital)

Scene composition:
- Center: A friendly robot character representing "AI Agent"
- Left side: A brain icon with gears labeled "スキル（脳みそ）"
- Right side: Robot arms/hands labeled "MCPツール（手足）"
- Arrows connecting brain and hands to the robot
- Simple equation at bottom: 脳みそ + 手足 = AIエージェント

Colors:
- White paper background
- Black outlines
- Yellow highlight on the robot
- Blue for brain/skills area
- Green for tools/hands area

Japanese Labels (must be readable):
- "AIエージェント" pointing to robot
- "スキル（脳みそ）" pointing to brain
- "MCPツール（手足）" pointing to hands
- "プロンプト・手順書" near brain
- "実行する道具" near hands

Key takeaway annotation (handwritten Japanese):
"AIに手足を与えると、自分で仕事ができるようになる！"
"""
    },
    {
        "id": "02_mcp_three_elements",
        "title": "MCPの3要素",
        "prompt": """Create a hand-drawn infographic explaining MCP (Model Context Protocol) components.

Style:
- Graphic recording / whiteboard art style
- Marker pens on white paper texture
- Educational, clear hierarchy

Scene composition:
- Top: USB-C cable icon with "MCP = AIのUSB-C規格" label
- Below: Three pillars/columns representing components
- Column 1: Document icon for "リソース"
- Column 2: Chat bubble icon for "プロンプト"
- Column 3: Wrench/tool icon for "ツール"
- An AI robot at the bottom connecting to all three

Colors:
- White background
- Black outlines
- Orange highlight on "ツール" (most important)
- Blue for "リソース"
- Green for "プロンプト"

Japanese Labels (must be readable):
- "MCP（Model Context Protocol）" as title
- "リソース" - データ提供
- "プロンプト" - テンプレート提供
- "ツール" - 実行機能 ※重要！
- "AI" pointing to robot

Key takeaway annotation:
"ツールだけじゃない！3つの要素を理解しよう"
"""
    },
    {
        "id": "03_skill_vs_tool",
        "title": "スキル vs MCPツール比較",
        "prompt": """Create a hand-drawn infographic comparing Skills and MCP Tools using a new employee metaphor.

Style:
- Graphic recording / whiteboard art style
- Split screen comparison layout
- Friendly stick figures

Scene composition:
- Left side: "スキル" area with stick figure reading a manual/book, brain icon above
- Right side: "MCPツール" area with stick figure using laptop, hand icon above
- Center dividing line
- Bottom: Both combining into a productive employee

Colors:
- White background
- Blue theme for Skills side
- Green theme for Tools side
- Yellow highlight on the combined employee

Japanese Labels (must be readable):
- "スキル = 脳みそ" (left header)
- "MCPツール = 手足" (right header)
- "業務マニュアル" on book
- "こうやって仕事するんだよ" speech bubble
- "このPC使っていいよ" speech bubble
- "プロンプト（柔軟）" under skills
- "プログラム（確実）" under tools

Key takeaway annotation:
"マニュアル（考え方）+ 道具（実行力）= 仕事ができる社員"
"""
    },
    {
        "id": "04_workflow_comparison",
        "title": "従来型 vs エージェント型",
        "prompt": """Create a hand-drawn infographic comparing traditional workflows vs agent-based workflows.

Style:
- Graphic recording / whiteboard art style
- Before/After comparison layout
- Clear visual contrast

Scene composition:
- Top half: "従来型" with complex flowchart, stressed person, red X mark
- Bottom half: "エージェント型" with simple Start → AI → Goal, happy person, green checkmark

Colors:
- White background
- Red/Orange for traditional (complexity)
- Green/Blue for agent-based (simplicity)
- Yellow highlight on the goal

Japanese Labels (must be readable):
- "従来のワークフロー" header
- "1から100まで全部決める..."
- "エージェント型" header
- "ゴールだけ伝える！"
- "道はAIが決める"

Key takeaway annotation:
"分岐を決めなくても、AIが最適な道を選ぶ時代へ"
"""
    },
    {
        "id": "05_summary_roadmap",
        "title": "エージェントマスターへの道",
        "prompt": """Create a hand-drawn infographic showing the roadmap to becoming an AI Agent master.

Style:
- Graphic recording / whiteboard art style
- Journey/roadmap visual metaphor
- Encouraging, motivational tone

Scene composition:
- Left: Stick figure at "今ここ" (You are here)
- Path going upward to the right with 4 milestones
- Top right: Triumphant figure with AI robot partner
- Stars around the goal

Colors:
- White background
- Path in orange/yellow
- Milestones in blue
- Goal area in green

Japanese Labels (must be readable):
- "AIエージェントマスターへの道" as title
- "今ここ" at start
- "Step 1: MCPを知る"
- "Step 2: スキルを作る"
- "Step 3: ツールを作る"
- "Step 4: 組み合わせる"
- "AIエージェント完成！" at goal
- "2025年はエージェント元年"

Key takeaway annotation:
"一歩ずつ進めば、あなたもAIエージェントマスターに！"
"""
    }
]


def generate_image(prompt_data: Dict) -> Optional[str]:
    """Generate a single infographic image"""
    print(f"\n🎨 Generating: {prompt_data['title']}...")
    
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=[prompt_data["prompt"]],
            config=types.GenerateContentConfig(
                response_modalities=["TEXT", "IMAGE"],
            ),
        )
        
        output_path = output_dir / f"{prompt_data['id']}.png"
        
        for part in response.parts:
            if hasattr(part, "text") and part.text:
                print(f"   📝 Response: {part.text[:100]}...")
            if hasattr(part, "inline_data") and part.inline_data:
                # Save image
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
    print("📊 インフォグラフィック一括生成")
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
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 生成結果サマリー")
    print("=" * 60)
    
    success_count = sum(1 for r in results if r["success"])
    print(f"成功: {success_count}/{len(results)}")
    
    for r in results:
        status = "✅" if r["success"] else "❌"
        print(f"  {status} {r['title']}: {r['path'] or 'Failed'}")
    
    print("\n完了！")


if __name__ == "__main__":
    main()
