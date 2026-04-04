import base64
import os
import uuid
import whisper
from src.config import settings

_model = None

def get_model():
    global _model
    if _model is None:
        _model = whisper.load_model(settings.WHISPER_MODEL)
    return _model

LANG_MAP = {
    "Hindi": "hi",
    "Tamil": "ta",
}

def transcribe(audio_base64: str, language: str) -> str:
    lang_code = LANG_MAP.get(language, "hi")
    tmp_path = f"/tmp/{uuid.uuid4()}.mp3"

    try:
        audio_bytes = base64.b64decode(audio_base64)
        with open(tmp_path, "wb") as f:
            f.write(audio_bytes)

        model = get_model()
        result = model.transcribe(
            tmp_path,
            language=lang_code,
            task="transcribe",
            fp16=False,
        )
        transcript = result.get("text", "").strip()
        if not transcript:
            raise RuntimeError("Whisper returned empty transcript")
        return transcript

    except Exception as e:
        raise RuntimeError(f"Transcription failed: {str(e)}")
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
