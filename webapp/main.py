"""画像解析デモ Web版 — FastAPI アプリ。

起動:
    プロジェクトルートで
        uvicorn webapp.main:app --reload
    ブラウザで http://127.0.0.1:8000 を開く。

デスクトップ版(analyze.py)の機能をブラウザから利用できるようにしたもの。
カメラは閲覧者のブラウザ(getUserMedia)を使用し、フレーム画像を
サーバへ送って AWS で解析する。
"""

import base64
import os

from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles

from . import analysis, features

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(BASE_DIR)
STATIC_DIR = os.path.join(BASE_DIR, "static")

app = FastAPI(title="画像解析デモ Web版")


# ---------------------------------------------------------------------------
# ヘルパー
# ---------------------------------------------------------------------------
def _decode_image(image_b64: str) -> bytes:
    """'data:image/...;base64,xxxx' もしくは素の base64 を bytes に。"""
    if not image_b64:
        raise HTTPException(status_code=400, detail="画像が指定されていません")
    if "," in image_b64:
        image_b64 = image_b64.split(",", 1)[1]
    try:
        return base64.b64decode(image_b64)
    except Exception:
        raise HTTPException(status_code=400, detail="画像のデコードに失敗しました")


def _read_text_file(name: str, default: str = "") -> str:
    path = os.path.join(PROJECT_DIR, name)
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return default


# ---------------------------------------------------------------------------
# ページ
# ---------------------------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
def index():
    path = os.path.join(STATIC_DIR, "index.html")
    with open(path, "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())


@app.get("/api/features")
def api_features():
    """デモ機能の一覧（並び順＝段階解放のステップ順）。"""
    return {"features": features.FEATURES}


@app.get("/api/defaults")
def defaults():
    """フォームの初期値（message.txt / questions.txt の内容）。"""
    return {
        "polly_text": _read_text_file(
            "message.txt", "こんにちは。音声合成のデモです。"
        ),
        "bedrock_prompt": _read_text_file(
            "questions.txt", "冬の北海道の楽しみ方を教えてください。"
        ),
    }


# ---------------------------------------------------------------------------
# 解析 API
# ---------------------------------------------------------------------------
@app.post("/api/detect")
def detect(mode: str = Form(...), image: str = Form(...)):
    """mode: face / label / text / trans / celeb"""
    if mode not in analysis.DETECTORS:
        raise HTTPException(status_code=400, detail=f"未対応のモード: {mode}")
    image_bytes = _decode_image(image)
    try:
        png_bytes, results, summary = analysis.analyze(mode, image_bytes)
    except analysis.ClientError as e:
        raise HTTPException(status_code=502, detail=f"AWSエラー: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    data_url = "data:image/png;base64," + base64.b64encode(png_bytes).decode()
    return JSONResponse({"image": data_url, "results": results, "summary": summary})


# ---------------------------------------------------------------------------
# 音声合成 API
# ---------------------------------------------------------------------------
@app.post("/api/polly")
def api_polly(
    text: str = Form(...),
    voice: str = Form("Kazuha"),
    speed: int = Form(100),
    engine: str = Form("neural"),
    use_ssml: bool = Form(True),
):
    try:
        mp3 = analysis.synthesize_speech(
            text, voice_id=voice, speed=speed,
            engine=engine, use_ssml_breaks=use_ssml,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return Response(content=mp3, media_type="audio/mpeg")


# ---------------------------------------------------------------------------
# 生成AI API
# ---------------------------------------------------------------------------
@app.post("/api/bedrock")
def api_bedrock(prompt: str = Form(...)):
    try:
        answer = analysis.invoke_bedrock(prompt)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"answer": answer}


# 静的ファイル（必要になった場合用）
if os.path.isdir(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
