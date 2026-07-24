"""顔検出 (AWS Rekognition detect_faces)。"""

from PIL import ImageDraw

from ..core import (
    draw_label,
    load_image,
    make_font,
    rekognition,
    to_png_bytes,
    to_rekognition_bytes,
)

GENDER_JA = {"Male": "男性", "Female": "女性", "Unknown": "不明"}
EMOTION_JA = {
    "HAPPY": "喜び",
    "SAD": "悲しみ",
    "ANGRY": "怒り",
    "CONFUSED": "困惑",
    "DISGUSTED": "嫌悪",
    "SURPRISED": "驚き",
    "CALM": "落ち着き",
    "FEAR": "恐れ",
    "UNKNOWN": "不明",
}


def detect_faces(image_bytes):
    img = load_image(image_bytes)
    resp = {"FaceDetails": []}  # TODO: rekognition().detect_faces(Image={"Bytes": to_rekognition_bytes(img)}, Attributes=["ALL"])
    # resp = rekognition().detect_faces(
    #     Image={"Bytes": to_rekognition_bytes(img)}, Attributes=["ALL"]
    # )
    draw = ImageDraw.Draw(img)
    w, h = img.size
    font = make_font(max(16, w // 45))
    results = []

    for fd in resp["FaceDetails"]:
        box = fd["BoundingBox"]
        left, top = int(box["Left"] * w), int(box["Top"] * h)
        bw, bh = int(box["Width"] * w), int(box["Height"] * h)
        draw.rectangle([left, top, left + bw, top + bh], outline=(255, 0, 0), width=3)
        emotion = "UNKNOWN"
        emotion_confidence = 0.0
        try:
            # labelにAgeRangeを入れる 大文字・小文字注意
            label = ""
            age = age = fd[label] if label != "" else {"Low": 0, "High": 100}
            # labelにValueを入れる 大文字・小文字注意
            label = ""
            gender = fd["Gender"][label] if label != "" else "Unknown"
            top_emotion = 0
            # top_emotion = max(fd["Emotions"], key=lambda e: e["Confidence"])
            # emotion = top_emotion["Type"]
            emotion_confidence = float(top_emotion.get("Confidence", 0.0))

            label = (
                f"{GENDER_JA.get(gender, gender)} {age['Low']}-{age['High']}歳 "
                f"{EMOTION_JA.get(emotion, emotion)} {emotion_confidence:.1f}%"
            )
            ty = top - font.size - 6
            if ty < 0:
                ty = top + 4
            draw_label(draw, (left, ty), label, font)
        except Exception:
            pass
        results.append(
            {
                "gender": GENDER_JA.get(gender, gender),
                "age": f"{age['Low']}-{age['High']}",
                "emotion": EMOTION_JA.get(emotion, emotion),
                "emotion_confidence": round(emotion_confidence, 1),
                "smile": bool(fd.get("Smile", {}).get("Value")),
                "confidence": round(fd["Confidence"], 1),
            }
        )

    summary = f"{len(results)} 人の顔を検出しました" if results else "顔は検出されませんでした"
    return to_png_bytes(img), results, summary
