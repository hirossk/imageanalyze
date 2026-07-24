"""AIガイド ― 複数サービスを「1枚の写真」を軸に連結する体験。

これまで単体で見せてきた機能（画像を見る=Claude vision、話す=Polly）を合体させる:
  1. 実況  : 写真を Claude が見て、明るく実況 → Polly が読み上げ
  2. 質問  : 写真について質問 → Claude が写真だけを根拠に回答 → Polly が読み上げ

生成テキストをそのまま Polly に渡すため、synthesize_speech は
use_ssml_breaks=False（平文モード）で呼ぶ（生成文に SSML 記法が紛れても誤作動しない）。
"""

from . import core, genai, speech

# 実況プロンプト
NARRATE_PROMPT = (
    "あなたは元気で親しみやすい実況ガイドです。"
    "この写真に写っているものを、日本語で明るく楽しく2〜3文で実況してください。"
    "話し言葉で、専門用語は避けてください。"
    "人物がいても名前を特定せず、雰囲気や様子を伝えてください。"
    "実況の言葉だけを出力し、前置きや注釈は書かないでください。"
)

# 写真Q&Aプロンプト（質問は後ろに連結。.format は使わず {} 混入を避ける）
CHAT_PREFIX = (
    "あなたは写真について答える親切なガイドです。"
    "この写真だけを根拠に、日本語で簡潔に(1〜3文)答えてください。"
    "写真から分からないことは「写真からは分かりません」と答えてください。"
    "答えの文だけを出力してください。\n質問："
)


def _prep(image_bytes):
    """受け取った画像を Claude/Polly 用に正規化（JPEGバイト列）。"""
    img = core.load_image(image_bytes)
    return core.to_rekognition_bytes(img)


def narrate(image_bytes, voice_id="Kazuha"):
    """写真を実況 → (実況テキスト, mp3バイト列)。"""
    jpeg = _prep(image_bytes)
    text = genai.invoke_bedrock_vision(jpeg, NARRATE_PROMPT)
    mp3 = speech.synthesize_speech(text, voice_id=voice_id, use_ssml_breaks=False)
    return text, mp3


def answer_about(image_bytes, question, voice_id="Kazuha"):
    """写真についての質問に回答 → (回答テキスト, mp3バイト列)。"""
    if not question or not question.strip():
        raise ValueError("質問が空です")
    jpeg = _prep(image_bytes)
    text = genai.invoke_bedrock_vision(jpeg, CHAT_PREFIX + question.strip())
    mp3 = speech.synthesize_speech(text, voice_id=voice_id, use_ssml_breaks=False)
    return text, mp3
