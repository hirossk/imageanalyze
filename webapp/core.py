"""共有インフラ: 設定・遅延AWSクライアント・画像変換・翻訳。

detectors/*・speech.py・genai.py の各機能モジュールが土台として使う層。
ここは特定の機能に依存しない（＝どの機能からも安全に import できる）。
"""

import io
import os

import boto3
from botocore.exceptions import ClientError  # 各モジュールが core.ClientError で使える
from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------------------
# 設定
# ---------------------------------------------------------------------------
REGION = os.getenv("AWS_REGION", "ap-northeast-1")            # Rekognition / Translate / Polly
BEDROCK_REGION = os.getenv("BEDROCK_REGION", "ap-northeast-1")     # Bedrock

BEDROCK_MODEL_ID = os.getenv(
    "BEDROCK_MODEL_ID", "anthropic.claude-sonnet-4-5-20250929-v1:0"
)
# ap-northeast-1(東京) では Claude Sonnet 4.5 の推論プロファイルは
# 'jp.'(日本国内) または 'global.'(グローバル)。'us.'/'apac.' は無効。
BEDROCK_INFERENCE_PROFILE_ID = os.getenv(
    "BEDROCK_INFERENCE_PROFILE_ID",
    "jp.anthropic.claude-sonnet-4-5-20250929-v1:0",
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_FONT_PATH = os.path.join(BASE_DIR, "fonts", "NotoSansCJK.ttc")


def _split_font_paths(value):
    if not value:
        return []
    return [p.strip() for p in value.split(os.pathsep) if p.strip()]


def _resolve_font_path():
    # 例:
    # FONT_PATH="C:\\fonts\\NotoSansThai-Regular.ttf"
    # FONT_PATHS="C:\\fonts\\NotoSansThai-Regular.ttf;C:\\fonts\\NotoSansCJK.ttc"
    candidates = []
    candidates.extend(_split_font_paths(os.getenv("FONT_PATH")))
    candidates.extend(_split_font_paths(os.getenv("FONT_PATHS")))
    candidates.append(DEFAULT_FONT_PATH)
    for path in candidates:
        if os.path.exists(path):
            return path
    return DEFAULT_FONT_PATH


FONT_PATH = _resolve_font_path()


# Rekognition に送る画像の最大辺（大きすぎる画像を縮小して 5MB 制限と速度に配慮）
MAX_SIDE = 1600

# ---------------------------------------------------------------------------
# AWS クライアント（遅延生成：認証情報が無い環境でも import は通る）
# ---------------------------------------------------------------------------
_clients = {}


def _client(service, region):
    key = (service, region)
    if key not in _clients:
        _clients[key] = boto3.client(service, region_name=region)
    return _clients[key]


def rekognition():
    return _client("rekognition", REGION)


def translate():
    return _client("translate", REGION)


def polly():
    return _client("polly", REGION)


def bedrock_runtime():
    return _client("bedrock-runtime", BEDROCK_REGION)


# ---------------------------------------------------------------------------
# 画像ユーティリティ
# ---------------------------------------------------------------------------
def load_image(image_bytes):
    """バイト列を RGB の PIL 画像に。"""
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    # 大きすぎる場合は縮小
    w, h = img.size
    scale = MAX_SIDE / max(w, h)
    if scale < 1:
        img = img.resize((int(w * scale), int(h * scale)))
    return img


def to_rekognition_bytes(pil_img):
    """Rekognition に渡す JPEG バイト列。"""
    buf = io.BytesIO()
    pil_img.save(buf, format="JPEG", quality=90)
    return buf.getvalue()


def to_png_bytes(pil_img):
    buf = io.BytesIO()
    pil_img.save(buf, format="PNG")
    return buf.getvalue()


def make_font(size):
    try:
        return ImageFont.truetype(FONT_PATH, size, index=0)
    except Exception:
        return ImageFont.load_default()


def draw_label(draw, xy, text, font, text_color=(255, 255, 255),
               bg_color=(25, 131, 255)):
    """背景付きテキストを描画（見やすさ確保）。"""
    if not text:
        return
    x, y = xy
    try:
        bbox = draw.textbbox((x, y), text, font=font)
        pad = 3
        draw.rectangle(
            [bbox[0] - pad, bbox[1] - pad, bbox[2] + pad, bbox[3] + pad],
            fill=bg_color,
        )
    except Exception:
        pass
    draw.text((x, y), text, fill=text_color, font=font)


def translate_to_ja(text , target_language_code="ja"):
    if not text:
        return text
    try:
        resp = translate().translate_text(
            Text=text, SourceLanguageCode="auto", TargetLanguageCode=target_language_code
        )
        return resp.get("TranslatedText", text)
    except Exception:
        return text
