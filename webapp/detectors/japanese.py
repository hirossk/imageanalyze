"""日本語よみとり (生成AI / Claude ビジョン)。

Rekognition の detect_text はラテン文字のみ対応で日本語(CJK)を読めないため、
マルチモーダルの Claude に画像を渡して OCR させる。
Claude は座標を返さないので、画像はそのまま返し、読み取ったテキストを一覧表示する。
"""

from ..core import load_image, to_rekognition_bytes, to_png_bytes
from ..genai import invoke_bedrock_vision

_PROMPT = (
    "この画像に写っている文字（日本語・英語など全て）を、書かれている順に"
    "1行ずつそのまま書き出してください。文字だけを出力し、説明・注釈・前置きは"
    "一切付けないでください。文字が全く無い場合は「（テキストなし）」とだけ答えてください。"
)


def read_japanese_text(image_bytes):
    img = load_image(image_bytes)
    text = invoke_bedrock_vision(to_rekognition_bytes(img), _PROMPT,
                                 media_type="image/jpeg")

    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    if lines == ["（テキストなし）"]:
        lines = []
    results = [{"text": ln} for ln in lines]
    summary = (f"{len(results)} 行のテキストを読み取りました"
               if results else "テキストは見つかりませんでした")
    return to_png_bytes(img), results, summary
