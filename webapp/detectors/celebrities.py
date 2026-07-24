"""有名人検出 (AWS Rekognition recognize_celebrities)。"""

from PIL import ImageDraw

from ..core import (
    rekognition, load_image, to_rekognition_bytes, to_png_bytes,
    make_font, draw_label,
)


def recognize_celebrities(image_bytes):
    img = load_image(image_bytes)

    resp = {"CelebrityFaces": []}  # TODO: rekognition().recognize_celebrities(Image={"Bytes": to_rekognition_bytes(img)})
    # resp = rekognition().recognize_celebrities(
    #     Image={"Bytes": to_rekognition_bytes(img)}
    # )
    draw = ImageDraw.Draw(img)
    w, h = img.size
    font = make_font(max(16, w // 45))
    results = []

    for celeb in resp.get("CelebrityFaces", []):
        box = celeb["Face"]["BoundingBox"]
        left, top = int(box["Left"] * w), int(box["Top"] * h)
        bw, bh = int(box["Width"] * w), int(box["Height"] * h)
        draw.rectangle([left, top, left + bw, top + bh],
                       outline=(255, 0, 0), width=3)
        ty = top - font.size - 6
        if ty < 0:
            ty = top + 4
        # draw_label(draw, (left, ty), celeb["Name"], font)
        # results.append({
        #     "name": celeb["Name"],
        #     "confidence": round(celeb.get("MatchConfidence", 0), 1),
        # })

    summary = (f"{len(results)} 人の有名人を検出しました"
               if results else "有名人は検出されませんでした")
    return to_png_bytes(img), results, summary
