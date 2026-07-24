"""オープンキャンパス デモの機能レジストリ（単一の情報源）。

このリストの **並び順がそのまま「段階的に解放していくステップの順番」** になる。
機能の追加・並び替え・文言変更は、原則このファイルだけを編集すればよい。

各要素:
  id    … 機能の識別子
  title … ボタン/見出しに出す名前
  desc  … 観客向けの一言説明（ステップバーに表示）
  kind  … "input" | "detect" | "polly" | "bedrock" | "guide"
  mode  … kind=="detect" のとき、analysis.DETECTORS のキー
"""

from . import analysis

FEATURES = [
    {"id": "input", "title": "カメラ / 画像入力", "kind": "input",
     "desc": "カメラで撮影するか、画像ファイルを選びます。"},
    {"id": "label", "title": "物体検出", "kind": "detect", "mode": "label",
     "desc": "写っているモノを日本語ラベルで一覧表示します。"},
    {"id": "face", "title": "顔検出", "kind": "detect", "mode": "face",
     "desc": "顔の位置・年齢・性別・感情を推定します。"},
    {"id": "jaocr", "title": "日本語よみとり", "kind": "detect", "mode": "jaocr",
     "desc": "生成AI(Claude)で日本語の文字を読み取ります。"},
    {"id": "trans", "title": "翻訳", "kind": "detect", "mode": "trans",
     "desc": "画像内テキストを検出して日本語訳を重ねます。"},
    {"id": "celeb", "title": "有名人検出", "kind": "detect", "mode": "celeb",
     "desc": "有名人を認識して名前を表示します。"},
    {"id": "polly", "title": "音声合成", "kind": "polly",
     "desc": "文章をAWS Pollyで自然な音声に変換します。"},
    {"id": "bedrock", "title": "生成AI", "kind": "bedrock",
     "desc": "生成AI(Claude)に質問して答えてもらいます。"},
    {"id": "guide", "title": "AIガイド（実況＆質問）", "kind": "guide",
     "desc": "AIが写真を見て実況し、質問にも答えます（生成AI＋音声の合体・フィナーレ）。"},
]

# step 番号を並び順から自動付与（手で振らなくてよい）
for _i, _f in enumerate(FEATURES, start=1):
    _f["step"] = _i

# detect 機能が analysis 側に実在するか検証（設定ミスを起動時に検出）
_missing = [f["mode"] for f in FEATURES
            if f["kind"] == "detect" and f["mode"] not in analysis.DETECTORS]
if _missing:
    raise RuntimeError(f"features.py: analysis.DETECTORS に無いモード: {_missing}")
