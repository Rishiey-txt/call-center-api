import base64
import os
import uuid
from groq import Groq
from src.config import settings

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

        client = Groq(api_key=settings.GROQ_API_KEY)

        with open(tmp_path, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                file=(tmp_path, audio_file.read()),
                model="whisper-large-v3",
                language=lang_code,
                response_format="text",
            )

        transcript = transcription.strip() if isinstance(transcription, str) else transcription.text.strip()
        if not transcript:
            raise RuntimeError("Groq returned empty transcript")
        return transcript

    except Exception as e:
        raise RuntimeError(f"Transcription failed: {str(e)}")
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
