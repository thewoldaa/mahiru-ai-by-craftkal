"""Google TTS helper."""
from gtts import gTTS


def synthesize(text: str, lang: str, output_path: str) -> str:
    tts = gTTS(text=text, lang=lang)
    tts.save(output_path)
    return output_path
