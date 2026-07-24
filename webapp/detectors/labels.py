"""物体検出 (AWS Rekognition detect_labels)。日本語ラベルは Translate で変換。"""

from PIL import ImageDraw

from ..core import (
    rekognition, load_image, to_rekognition_bytes, to_png_bytes,
    make_font, draw_label, translate_to_ja,
)


def detect_labels(image_bytes):
    img = load_image(image_bytes)
    resp = {"Labels": []}  # TODO: rekognition().detect_labels(Image={"Bytes": to_rekognition_bytes(img)}, MaxLabels=15)
    # resp = rekognition().detect_labels(
    #     Image={"Bytes": to_rekognition_bytes(img)}, MaxLabels=15
    # )
    draw = ImageDraw.Draw(img)
    w, h = img.size
    font = make_font(max(16, w // 45))
    results = []

    top = 8
    for label in resp["Labels"]:
        name = label["Name"]
        name_ja = label["Name"]  # TODO: Translate で日本語化する
        # name_ja = translate_to_ja(label["Name"])
        conf = label["Confidence"]
        draw_label(draw, (10, top),
                   f"{name_ja} : {conf:.1f}%", font)
        top += font.size + 8
        results.append({
            "name": name,
            "name_ja": name_ja,
            "confidence": round(conf, 1),
        })

    summary = f"{len(results)} 個のラベルを検出しました"
    return to_png_bytes(img), results, summary
