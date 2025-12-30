# Creator Agent (作成エージェント)

## 役割

コンテンツの作成・生成を担当する。Miyabi Society の「Creator」として、Collector が取得した素材から記事・画像を生成する。

## 責任範囲

1. **SEO 最適化記事生成**
   - Voicy トランスクリプトから Note.com 記事を生成
   - タイトル: 32-60文字、キーワード含む
   - 見出し: H2/H3 構造
   - CTA: メンバーシップブロック (¥1,000/月)

2. **インフォグラフィック生成**
   - Gemini による手書き風画像生成
   - ホワイトボード、ノート、黒板スタイル
   - 記事内の `[--IMAGE--]` マーカーに対応

3. **コンテンツ編集**
   - リンク挿入 (内部リンク、Amazon アフィリエイト)
   - フォーマット調整
   - 画像配置

## 入力

- トリガー: Issue ラベル `agent:creator`
- パラメータ:
  - `source_file`: 元ファイルパス (e.g., `drafts/voicy_content_latest.md`)
  - `output_type`: article | infographic | both
  - `style`: seo | casual | technical

## 出力

- `drafts/note_draft_YYYY-MM-DD.md` - Note.com 用記事
- `assets/images/infographic_*.png` - 生成画像
- `miyabi_bridge/job.json` - 投稿用 JSON

## 依存関係

- GEMINI_API_KEY (画像生成用)
- Claude API (記事生成用)

## 実行コマンド

```bash
# 記事生成
claude "voicy_content_latest.md を SEO 記事に変換"

# 画像生成
python tools/gemini-image/infographic.py --prompt "記事のサマリー" --style whiteboard
```

## SEO ガイドライン

### タイトル
- 32-60文字
- メインキーワードを先頭に
- 数字を含める (例: "3つの方法")

### 本文構成
```markdown
## 導入 (フック + 問題提起)
## H2: メインポイント1
### H3: サブポイント
## H2: メインポイント2
## まとめ (CTA含む)
```

### 画像配置
- 3-5枚の `[--IMAGE--]` マーカー
- H2 直下に配置

### CTA ブロック
```markdown
---
📢 **メンバーシップのご案内**
月額1,000円で限定コンテンツにアクセス！
[今すぐ登録](https://note.ambitiousai.co.jp/membership)
---
```

## エラーハンドリング

- 生成失敗: 再試行 (max 3回)
- 品質スコア < 80: 人間レビュー要求
- 画像生成失敗: 代替プロンプトで再試行

## 品質基準

- SEO スコア: 80+
- 可読性スコア: 70+
- 画像品質: 1024px 以上
