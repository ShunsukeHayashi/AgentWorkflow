# Gemini Image Tools

Gemini 3 Pro Image Preview を使用した画像生成ツール群

## セットアップ

```bash
# 依存関係インストール
pip install -r requirements.txt

# 環境変数設定
export GEMINI_API_KEY=your_api_key
# または .env ファイルに記載
```

## ツール一覧

### 1. generate.py - 画像生成

```bash
# 基本的な画像生成
python generate.py "美しい夕日の風景" -o sunset.png

# 高解像度4K出力
python generate.py "プロフェッショナルな製品写真" -o product.png -s 4K -a 3:2

# Google検索グラウンディング
python generate.py "今日の東京の天気を可視化" --search -a 16:9

# Flashモデル（高速・低コスト）
python generate.py "シンプルなアイコン" -m flash
```

### 2. edit.py - 画像編集

```bash
# 要素追加
python edit.py "この画像に帽子を追加して" -i input.png -o output.png

# スタイル変換
python edit.py "この写真をダヴィンチ風の絵画に変換" -i photo.png

# 複数参照画像使用（Proのみ、最大14枚）
python edit.py "これらの人物を組み合わせて" -i base.png --refs person1.png person2.png
```

### 3. chat.py - マルチターンチャット

```bash
# インタラクティブセッション開始
python chat.py

# オプション付き
python chat.py -m pro -a 16:9 -s 2K --search
```

**チャット内コマンド:**
- `/quit` or `/exit` - 終了
- `/aspect 16:9` - アスペクト比変更
- `/size 4K` - 解像度変更
- `/image path.png メッセージ` - 画像添付

### 4. infographic.py - 手書き風インフォグラフィック

```bash
# シンプルな使用法
python infographic.py "Kubernetesの仕組み"

# スタイル指定
python infographic.py "APIの設計" --style whiteboard

# YAML設定ファイル使用
python infographic.py --yaml config.yaml

# プロンプト確認
python infographic.py "Git Flow" --show-prompt
```

**スタイルプリセット:**
- `notebook` - ノート風手書き
- `whiteboard` - ホワイトボード風
- `minimal` - ミニマルデザイン

## YAML設定ファイル例

```yaml
concept: "Dockerコンテナの仕組み"
style: notebook
aspect_ratio: "16:9"
image_size: "2K"
output: "docker.png"

labels:
  - text: "コンテナ"
    target: "isolated boxes"
  - text: "ホストOS"
    target: "base layer"

annotation: "各コンテナは独立！"

custom_elements: |
  - Show containers as rooms
  - Friendly stick figures
```

## アスペクト比

| 比率 | 用途 |
|------|------|
| 1:1 | SNS投稿、アイコン |
| 16:9 | プレゼン、動画サムネイル |
| 9:16 | ストーリーズ、縦動画 |
| 4:3 | 従来のスライド |
| 3:2 | 写真プリント |

## 解像度（Proモデルのみ）

| サイズ | ピクセル（1:1時） |
|--------|------------------|
| 1K | 1024×1024 |
| 2K | 2048×2048 |
| 4K | 4096×4096 |

## 環境変数

```bash
# .env ファイル
GEMINI_API_KEY=your_api_key_here
```
