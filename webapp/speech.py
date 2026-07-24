"""音声合成 (Amazon Polly)。"""

import re
import html

from .core import polly


def synthesize_speech(text, voice_id="Kazuha", speed=100,
                      engine="neural", use_ssml_breaks=True):
    """テキストを mp3 バイト列に。

    use_ssml_breaks=True のとき、message.txt 互換の記法を解釈する:
      - 'bt=2s' → 2秒の無音
      - 'VoiceId' → 選択中の音声名に置換
    """
    if not text or not text.strip():
        raise ValueError("テキストが空です")

    engine = engine or "standard"

    if use_ssml_breaks:
        safe = html.escape(text)                       # & < > をエスケープ
        safe = re.sub(r"bt=(\d+)s", r'<break time="\1s"/>', safe)
        safe = safe.replace("VoiceId", voice_id)
        payload = f'<speak><prosody rate="{int(speed)}%">{safe}</prosody></speak>'
        resp = polly().synthesize_speech(
            Text=payload, OutputFormat="mp3", TextType="ssml",
            VoiceId=voice_id, Engine=engine,
        )
    else:
        resp = polly().synthesize_speech(
            Text=text, OutputFormat="mp3",
            VoiceId=voice_id, Engine=engine,
        )

    if "AudioStream" not in resp:
        raise RuntimeError("音声データを取得できませんでした")
    return resp["AudioStream"].read()
