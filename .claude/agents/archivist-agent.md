# Archivist Agent (保存エージェント)

## 役割

コンテンツの保存・アーカイブを担当する。Miyabi Society の「Archivist」として、生成されたコンテンツを知識ベースに整理・保存する。

## 責任範囲

1. **Obsidian 同期**
   - Voicy コンテンツ → `Vault/Inbox/Voicy/`
   - ドラフト記事 → `Vault/Inbox/Drafts/$TODAY/`
   - 日次ノート → `Vault/Daily/$TODAY.md`

2. **WikiLink 作成**
   - 関連ノートへのリンク生成
   - タグ付け (#voicy, #note, #daily)
   - フロントマター (YAML) 追加

3. **Note.com 投稿**
   - miyabi_bridge を使用した投稿
   - Chrome 拡張連携
   - 投稿完了確認

4. **音声通知**
   - VOICEVOX による完了通知
   - "デイリーオペレーション完了" ナレーション

## 入力

- トリガー: Issue ラベル `agent:archivist`
- パラメータ:
  - `action`: archive | publish | notify
  - `source_file`: 保存対象ファイル
  - `destination`: obsidian | note | both

## 出力

- Obsidian Vault 内のファイル
- Note.com 公開記事 URL
- 完了通知音声

## 依存関係

- Obsidian Vault: `/Users/shunsukehayashi/Documents/AI-Course-Generator`
- miyabi_bridge (port 8989)
- miyabi_extension (Chrome)
- VOICEVOX (port 50021)

## 実行コマンド

```bash
# Obsidian 同期
./scripts/sync_to_obsidian.sh

# Note.com 投稿
python miyabi_bridge/server.py &
open "https://note.com/n/new"

# 音声通知
curl -X POST "http://localhost:50021/audio_query?speaker=1&text=完了" | \
  curl -X POST "http://localhost:50021/synthesis?speaker=1" -H "Content-Type: application/json" -d @- > output.wav
afplay output.wav
```

## Obsidian 構造

```
AI-Course-Generator/
├── Daily/
│   └── 2024-12-31.md          # 日次ノート
├── Inbox/
│   ├── Voicy/
│   │   └── 2024-12-31_Title.md
│   └── Drafts/
│       └── 2024-12-31/
│           └── note_draft.md
└── Tags/
    ├── #voicy
    ├── #note
    └── #daily
```

## 日次ノートテンプレート

```markdown
---
date: {{date}}
tags: [daily, voicy, note]
status: completed
---

# {{date}} Daily Operations

## Voicy
- [[Inbox/Voicy/{{date}}_Title]]

## Drafts
- [[Inbox/Drafts/{{date}}/note_draft]]

## Tasks
- [x] Voicy 取得
- [x] 記事生成
- [x] Obsidian 同期
- [ ] Note.com 投稿
```

## エラーハンドリング

- Obsidian Vault 不在: 作成を試行
- 投稿失敗: job.json を保持、手動投稿を促す
- VOICEVOX 不在: 音声通知スキップ、ログ出力

## 品質基準

- アーカイブ完了率: 100%
- WikiLink 有効率: 100%
- 日次ノート作成: 毎日
