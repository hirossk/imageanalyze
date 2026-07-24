"""後方互換ファサード。

実装は機能ごとにモジュール分割済み:
  core.py        共有（設定・AWSクライアント・画像変換・翻訳）
  detectors/     検出6種 + DETECTORS / analyze()
  speech.py      音声合成（Polly）
  genai.py       生成AI（Bedrock）

既存の呼び出し（`from . import analysis; analysis.DETECTORS` など）を壊さないよう、
主要シンボルをここで再エクスポートする。新規コードは各モジュールを直接 import してよい。
"""

# main.py が `analysis.ClientError` を参照するため再エクスポート
from botocore.exceptions import ClientError  # noqa: F401

from .core import (  # noqa: F401
    REGION, BEDROCK_REGION, BEDROCK_MODEL_ID, BEDROCK_INFERENCE_PROFILE_ID,
    rekognition, translate, polly, bedrock_runtime,
    load_image, to_rekognition_bytes, to_png_bytes, translate_to_ja,
)
from .detectors import DETECTORS, analyze  # noqa: F401
from .speech import synthesize_speech  # noqa: F401
from .genai import invoke_bedrock, invoke_bedrock_vision  # noqa: F401
