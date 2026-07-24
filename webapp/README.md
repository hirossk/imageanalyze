# 画像解析デモ Web版（FastAPI）

デスクトップ版（`analyze.py` / `util.py`、TkEasyGUI）の機能を、ブラウザから使える
Webアプリにしたものです。既存のデスクトップ版はそのまま残しています。

## 機能

| 機能 | 使用サービス |
|------|------------|
| 顔検出（年齢・性別・感情） | AWS Rekognition |
| 物体検出（日本語ラベル） | Rekognition + Translate |
| テキスト検出 | Rekognition |
| テキスト翻訳（画像内文字を和訳表示） | Rekognition + Translate |
| 有名人検出 | Rekognition |
| 音声合成 | AWS Polly |
| 生成AI | AWS Bedrock（Claude Sonnet 4.5） |

カメラは**ブラウザ側**（`getUserMedia`）を使用します。画像ファイルのアップロードにも対応。

## セットアップ

```powershell
# 依存関係のインストール（プロジェクトの仮想環境を利用）
.\Scripts\python.exe -m pip install -r webapp\requirements-web.txt
```

AWS 認証情報（`aws configure` 等）と、対象サービスへのアクセス権が必要です。

## 起動

```powershell
# 方法1: スクリプト
.\webapp\run.ps1

# 方法2: 直接
.\Scripts\python.exe -m uvicorn webapp.main:app --host 127.0.0.1 --port 8000 --reload
```

ブラウザで <http://127.0.0.1:8000> を開きます。

> カメラを使う場合、ブラウザは `localhost`／`https` でのみカメラを許可します。
> `127.0.0.1` / `localhost` で開けば問題ありません。

## 環境変数（任意）

| 変数 | 既定値 | 用途 |
|------|--------|------|
| `AWS_REGION` | `ap-northeast-1` | Rekognition / Translate / Polly |
| `BEDROCK_REGION` | `us-east-1` | Bedrock |
| `BEDROCK_INFERENCE_PROFILE_ID` | `us.anthropic.claude-sonnet-4-5-...` | Bedrock 推論プロファイル |

## 構成

```
webapp/
  main.py              FastAPI アプリ（ルーティング）
  features.py          機能レジストリ（並び順＝段階解放ステップ順）
  core.py              共有: 設定・AWSクライアント・画像変換・翻訳
  detectors/           検出（1機能=1ファイル）
    __init__.py          DETECTORS レジストリ + analyze()
    faces.py  labels.py  text.py  japanese.py  celebrities.py
  speech.py            音声合成（Polly）
  genai.py             生成AI（Bedrock / Claude）
  analysis.py          後方互換ファサード（上記を re-export）
  static/index.html    フロントエンド（カメラ・UI 一式、Api クライアント）
  requirements-web.txt 依存関係
  run.ps1              起動スクリプト
```

機能を1つ足すときは、`detectors/` に1ファイル追加 → `detectors/__init__.py` の
`DETECTORS` に1行 → `features.py` にステップ登録、の3手順。
