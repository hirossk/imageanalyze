"""テキスト検出・翻訳 (AWS Rekognition detect_text)。

Rekognition のテキスト検出はラテン文字向け。日本語の読み取りは detectors/japanese.py 参照。
"""

from PIL import ImageDraw, ImageFont

from ..core import (
    rekognition, load_image, to_rekognition_bytes, to_png_bytes,
    make_font, draw_label, translate_to_ja,
)


def make_latin_font(size):
    """タイ語表示に対応したフォントを優先して作成。"""
    latin_font_candidates = [
        "C:/Windows/Fonts/tahoma.ttf",
        "C:/Windows/Fonts/leelawui.ttf",
        "C:/Windows/Fonts/cordia.ttf",
    ]
    for font_path in latin_font_candidates:
        try:
            return ImageFont.truetype(font_path, size)
        except Exception:
            continue
    return make_font(size)


def detect_text(image_bytes):
    img = load_image(image_bytes)
    resp = rekognition().detect_text(Image={"Bytes": to_rekognition_bytes(img)})
    draw = ImageDraw.Draw(img)
    w, h = img.size
    results = []

    for det in resp["TextDetections"]:
        if det["Type"] != "LINE":
            continue
        box = det["Geometry"]["BoundingBox"]
        left, top = int(box["Left"] * w), int(box["Top"] * h)
        bw, bh = int(box["Width"] * w), int(box["Height"] * h)
        draw.rectangle([left, top, left + bw, top + bh],
                       outline=(0, 200, 0), width=2)
        results.append({
            "text": det["DetectedText"],
            "confidence": round(det["Confidence"], 1),
        })

    summary = f"{len(results)} 行のテキストを検出しました"
    return to_png_bytes(img), results, summary


def translate_text(image_bytes):
    """画像内テキストを検出して日本語訳を重ねて表示。"""
    img = load_image(image_bytes)
    resp = {"TextDetections": []}  # TODO: rekognition().detect_text(Image={"Bytes": to_rekognition_bytes(img)})
    resp = rekognition().detect_text(Image={"Bytes": to_rekognition_bytes(img)})
    draw = ImageDraw.Draw(img)
    w, h = img.size
    
    # font = make_latin_font(max(16, w // 45))
    font = make_font(max(16, w // 45))
    results = []

    for det in resp["TextDetections"]:
        if det["Type"] != "LINE":
            continue
        original = det["DetectedText"]
        box = det["Geometry"]["BoundingBox"]
        left, top = int(box["Left"] * w), int(box["Top"] * h)
        # 言語コード一覧: https://docs.aws.amazon.com/translate/latest/dg/what-is-languages.html
        # ko韓国語、frフランス語、deドイツ語、esスペイン語、itイタリア語、ptポルトガル語、ruロシア語、zh中国語
        translated = translate_to_ja(original,"ja")
        draw_label(draw, (left, top), translated, font,
                   bg_color=(25, 131, 255))
        results.append({"original": original, "translated": translated})

    summary = f"{len(results)} 行のテキストを翻訳しました"
    return to_png_bytes(img), results, summary
