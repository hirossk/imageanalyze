"""生成AI (Amazon Bedrock / Claude) 呼び出し。"""

import json
import base64

from botocore.exceptions import ClientError

from .core import (
    bedrock_runtime,
    BEDROCK_INFERENCE_PROFILE_ID,
    BEDROCK_MODEL_ID,
)

_PROFILE_HINT = (
    "このモデルはオンデマンド呼び出し非対応です。"
    "環境変数 BEDROCK_INFERENCE_PROFILE_ID に Inference Profile の "
    "ID または ARN を設定してください。"
)


def _invoke(body):
    """Bedrock invoke_model の共通処理（プロファイル未設定エラーを分かりやすく変換）。"""
    model_id = BEDROCK_INFERENCE_PROFILE_ID or BEDROCK_MODEL_ID
    try:
        resp = bedrock_runtime().invoke_model(
            modelId=model_id,
            body=json.dumps(body).encode("utf-8"),
            contentType="application/json",
        )
    except ClientError as error:
        message = str(error)
        if ("on-demand throughput isn't supported" in message
                or "inference profile" in message.lower()):
            raise RuntimeError(_PROFILE_HINT) from error
        raise

    response_body = json.loads(resp["body"].read().decode("utf-8"))
    return response_body["content"][0]["text"]


def invoke_bedrock(prompt, max_tokens=2000, temperature=0.7):
    if not prompt or not prompt.strip():
        raise ValueError("プロンプトが空です")

    return _invoke({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": max_tokens,
        "temperature": temperature,
        "messages": [{"role": "user", "content": prompt}],
    })


def invoke_bedrock_vision(image_bytes, prompt, media_type="image/jpeg",
                          max_tokens=2000, temperature=0.0):
    """画像＋プロンプトを Claude(Bedrock) に渡し、テキスト応答を返す。"""
    b64 = base64.b64encode(image_bytes).decode("ascii")
    return _invoke({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": max_tokens,
        "temperature": temperature,
        "messages": [{
            "role": "user",
            "content": [
                {"type": "image", "source": {
                    "type": "base64", "media_type": media_type, "data": b64}},
                {"type": "text", "text": prompt},
            ],
        }],
    })
