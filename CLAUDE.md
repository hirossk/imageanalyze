# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

AWS を使った画像解析デモアプリ。オープンキャンパス等での実演を想定した教材的なコード。
同じ AWS 機能に対して **2つのフロントエンド** が存在する:

1. **デスクトップ版** (`analyze.py` + `util.py`) — TkEasyGUI + OpenCV。サーバ(PC)のカメラを直接使う。
2. **Web版** (`webapp/`) — FastAPI。カメラはブラウザ側(`getUserMedia`)を使い、フレームをサーバへ送って解析する。

両者は独立しており、Web版はデスクトップ版のファイルを一切変更していない。共有しているのは
ルート直下のアセット(`fonts/`、`message.txt`、`questions.txt`)のみ。

## 重要: 仮想環境がプロジェクトルート

**このリポジトリのルート自体が Python venv** になっている(`pyvenv.cfg`、`Scripts/`、`Lib/`、`Include/` が
ルートに存在)。Python は必ず `Scripts/python.exe` を使うこと。`Scripts/`・`Lib/`・`Include/`・`pyvenv.cfg`
は `.gitignore` 済みで、これらを編集・コミットしないこと。

```powershell
# 依存関係
.\Scripts\python.exe -m pip install -r requirement.txt          # デスクトップ版
.\Scripts\python.exe -m pip install -r webapp\requirements-web.txt  # Web版
```

## 実行

```powershell
# デスクトップ版 (GUI)
.\Scripts\python.exe analyze.py

# Web版 (ブラウザで http://127.0.0.1:8000)
.\webapp\run.ps1
# または
.\Scripts\python.exe -m uvicorn webapp.main:app --host 127.0.0.1 --port 8000 --reload
```

テストは存在しない。動作確認は実際に AWS を呼び出して行う(下記「動作確認」参照)。

## AWS への依存

全機能が AWS 実サービスを呼ぶ。ローカルにモックは無い。認証情報(`aws configure` 等)と各サービスへの
アクセス権が必須。使用サービスとリージョン:

- **Rekognition / Translate / Polly** — `ap-northeast-1`(東京)
- **Bedrock** — 既定は `ap-northeast-1`(東京)。モデルは Claude Sonnet 4.5 を **Inference Profile 経由** で呼ぶ。
  **プロファイルのプレフィックスがリージョン依存**で、東京では `jp.`(日本国内)または `global.`、
  `us.`/`apac.` は `The provided model identifier is invalid` になる(4.5 の `apac.` 版は存在しない)。
  既定は `jp.anthropic.claude-sonnet-4-5-20250929-v1:0`。オンデマンド呼び出しは非対応。
  環境変数 `BEDROCK_REGION` / `BEDROCK_INFERENCE_PROFILE_ID` / `BEDROCK_MODEL_ID` で上書き可。
  利用可能なプロファイルは `boto3.client('bedrock').list_inference_profiles()` で確認できる。

## アーキテクチャの要点

### デスクトップ版のロジックは util.py に集約
`util.py` が画面部品(TkEasyGUI ウィジェット)・AWS クライアント・描画ヘルパ・Polly/Bedrock 呼び出しを
すべて持つ。`analyze.py` は `from util import *` でそれを取り込み、`main()` のイベントループと
各 `*_detect()` 関数を定義する。デスクトップ版の描画は座標を `DIMW=800 / DIMH=600` 固定でスケールする
(`getDim()`)ため、実画像サイズとは無関係な前提になっている点に注意。

### Web版はGUIロジックを純粋関数へ再構成し、機能ごとにモジュール分割
Web版の AWS ロジックは util.py と同じ機能を「**画像バイト → (注釈済みPNG, 結果JSON, サマリ文字列)**」
を返す純粋関数として書き直したもの(GUI・OpenCV 非依存、描画は PIL のみ)。デスクトップ版と違い、
バウンディングボックスは **受信画像の実サイズ** に合わせて正規化座標を変換する。

実装は機能ごとに分割されている:
- `webapp/core.py` … 共有インフラ。設定・遅延AWSクライアント(`_client()`、認証情報が無くても import は通る)・
  画像変換(`load_image`/`to_rekognition_bytes`/`to_png_bytes`)・描画(`make_font`/`draw_label`)・`translate_to_ja`。
  **機能に依存しない土台**で、他のどのモジュールからも安全に import できる。
- `webapp/detectors/` … 検出1機能=1ファイル(`faces`/`labels`/`text`/`japanese`/`celebrities`)。
  `__init__.py` が各関数を集めて `DETECTORS` dict(`face`/`label`/`text`/`trans`/`celeb`/`jaocr`)と `analyze()` を公開。
- `webapp/speech.py` … 音声合成(Polly)。`webapp/genai.py` … 生成AI(Bedrock、`invoke_bedrock`/`invoke_bedrock_vision`)。
- `webapp/analysis.py` … **後方互換ファサード**。上記を re-export するだけ(`analysis.DETECTORS` 等の既存参照を維持)。
  依存方向は `detectors → (core, genai)`、`genai/speech → core` の一方向で循環しない。

`jaocr`(日本語よみとり、`detectors/japanese.py`)だけは Rekognition ではなく **Claude のビジョン機能**
(`genai.invoke_bedrock_vision()`)を使う。Rekognition の `detect_text` はラテン文字のみ対応で日本語(CJK)を
読めないため、画像を Claude に渡して OCR させている。Claude は座標を返さないので画像は無加工で返し、読み取った各行を results に入れる。

### 機能レジストリ＝段階解放の単一の情報源
`webapp/features.py` の `FEATURES` リストが全機能の並び順・表示名・説明の唯一の定義。
**リストの順番がそのままオープンキャンパス用「段階解放ステップ」の順番**になり、`step` 番号は
並び順から自動採番される。機能の追加・並び替え・文言変更はこのファイルだけ編集する
(detect 系は `analysis.DETECTORS` に実在するか import 時に検証される)。`/api/features` で公開。

### Web版のリクエスト経路
`webapp/main.py`(FastAPI, ルーティングのみ) → `webapp/analysis.py`(AWS ロジック)。
フロントの `webapp/static/index.html` は単一ファイルの自己完結 SPA。**サーバ呼び出しは JS の `Api`
オブジェクトに集約**(`Api.detect/polly/bedrock/features/defaults`)。カメラ/ファイル画像を base64
dataURL 化し、`multipart/form-data` の `image` フィールドで送る(カメラ・ファイルとも同一経路)。
サーバは注釈済み画像を data URL(base64 PNG)で返す(Polly のみバイナリ mp3)。起動時に `/api/features`
を読み、Step1(input)だけ表示した状態から「次の機能へ」で1つずつ解放する。フォームの初期値
(`message.txt`/`questions.txt`)は `/api/defaults` が返す。

### message.txt / questions.txt の役割
- `message.txt` — Polly 音声合成の入力サンプル。独自記法を持つ: `bt=2s` → `<break time="2s"/>`(無音)、
  `VoiceId` → 選択中の音声名に置換。この SSML 変換ロジックはデスクトップ版 `call_polly()` と
  Web版 `synthesize_speech()` の両方にある。
- `questions.txt` — Bedrock への質問サンプル。デスクトップ版は回答を `answer.txt` に書き出してから
  Polly で読み上げる(`answer.txt` は `.gitignore` 済み)。

## 日本語フォント
テキスト描画は `fonts/NotoSansCJK.ttc`(約18MB、リポジトリに含む)に依存。パスは
デスクトップ版が相対(`fonts\\NotoSansCJK.ttc`)、Web版はプロジェクトルートからの絶対パスを算出。

## 動作確認(スモークテスト)
サーバ起動後、curl で各エンドポイントを叩ける。**Windows の shell/Python print は cp932 で
文字化けする**ため、日本語を含む確認は curl の生バイト出力(`--data-urlencode "prompt@file"`)を使うこと。
実際に AWS 課金が発生する点に留意。
