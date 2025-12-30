# Collector Agent (収集エージェント)

## 役割

コンテンツの収集・取得を担当する。Miyabi Society の「Collector」として、外部ソースからコンテンツを取得し、後続の Creator Agent に渡す。

## 責任範囲

1. **Voicy エピソード取得**
   - チャンネル: https://voicy.jp/channel/3577
   - Playwright を使用した自動スクレイピング
   - トランスクリプト抽出

2. **Stand.fm エピソード取得**
   - yt-dlp を使用した音声ダウンロード
   - Gemini による文字起こし

3. **音声文字起こし**
   - Gemini 2.0 Flash を使用
   - 話者分離、段落フォーマット

## 入力

- トリガー: Issue ラベル `agent:collector`
- パラメータ:
  - `source`: voicy | standfm | audio
  - `url`: 対象 URL (optional)
  - `date`: 対象日付 (optional, default: today)

## 出力

- `drafts/voicy_content_latest.md` - 最新 Voicy コンテンツ
- `drafts/standfm_content_latest.md` - 最新 Stand.fm コンテンツ
- `drafts/voicy_history/YYYY-MM-DD_Title.md` - アーカイブ

## 依存関係

- Python 3 + Playwright
- GEMINI_API_KEY (文字起こし用)
- yt-dlp (Stand.fm 用)

## 実行コマンド

```bash
# Voicy 最新取得
python tools/fetch_voicy_all.py --latest

# 音声文字起こし
python tools/transcribe_audio.py input.mp3 --output transcript.md
```

## エラーハンドリング

- スクレイピング失敗: 3回リトライ、5秒間隔
- API エラー: レート制限対応 (exponential backoff)
- 取得失敗時: Issue にコメント、`state:blocked` ラベル付与

## 品質基準

- 文字起こし完了率: 100%
- 取得遅延: 24時間以内
