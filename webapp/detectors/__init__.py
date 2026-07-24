"""検出機能のレジストリ。

各検出は「画像バイト → (注釈済みPNG, 結果JSON, サマリ文字列)」を返す。
機能を追加したら、対応するファイルを作って下の DETECTORS に1行足すだけ
（さらに webapp/features.py にステップとして登録する）。
"""

from .faces import detect_faces
from .labels import detect_labels
from .text import detect_text, translate_text
from .japanese import read_japanese_text
from .celebrities import recognize_celebrities

# モード名 → 関数
DETECTORS = {
    "face": detect_faces,
    "label": detect_labels,
    "text": detect_text,
    "trans": translate_text,
    "celeb": recognize_celebrities,
    "jaocr": read_japanese_text,
}


def analyze(mode, image_bytes):
    if mode not in DETECTORS:
        raise ValueError(f"未対応のモード: {mode}")
    return DETECTORS[mode](image_bytes)
