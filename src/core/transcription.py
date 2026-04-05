import base64
import os
import re
import uuid
from groq import Groq
from src.config import settings

LANG_MAP = {
    "Hindi": "hi",
    "Tamil": "ta",
}

# Detect if text contains significant Tamil/Devanagari unicode script
def _has_native_script(text: str) -> bool:
    # Tamil unicode block: U+0B80–U+0BFF
    # Devanagari: U+0900–U+097F
    native = sum(1 for c in text if '\u0B80' <= c <= '\u0BFF' or '\u0900' <= c <= '\u097F')
    return native > 10  # more than 10 native script chars = needs transliteration


def _transliterate_to_roman(text: str, language: str) -> str:
    """
    Post-process: if Whisper still returned native script,
    use Gemini to convert it to romanized Tanglish/Hinglish.
    """
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=settings.GEMINI_API_KEY)

    lang_label = "Tamil" if language == "Tamil" else "Hindi"
    example = (
        "Vanakkam ma, neenga GUVI course-la interest irukeenga? "
        "Unga outstanding EMI 5000 rupees iruku."
        if language == "Tamil"
        else "Namaste ji, aapka outstanding EMI 5000 rupees hai."
    )

    prompt = f"""Transliterate the following {lang_label} text into romanized {lang_label} \
({lang_label} words written in English letters, also called \
{'Tanglish' if language == 'Tamil' else 'Hinglish'}).

Rules:
- Keep English words exactly as they are.
- Only convert native script characters to their phonetic English equivalent.
- Do NOT translate — just romanize.
- Return ONLY the transliterated text, no explanation.

Example output style: "{example}"

Text to transliterate:
{text}"""

    response = client.models.generate_content(
        model="gemini-1.5-flash",
        config=types.GenerateContentConfig(temperature=0.1),
        contents=prompt,
    )
    return response.text.strip()


def transcribe(audio_base64: str, language: str) -> str:
    lang_code = LANG_MAP.get(language, "hi")
    tmp_path = f"/tmp/{uuid.uuid4()}.mp3"

    try:
        audio_bytes = base64.b64decode(audio_base64)
        with open(tmp_path, "wb") as f:
            f.write(audio_bytes)

        client = Groq(api_key=settings.GROQ_API_KEY)

        # Prompt nudges Whisper toward romanized output for code-switched audio
        romanize_hint = (
            "Transcribe in Tanglish (Tamil words written in English letters). "
            "Example: 'Vanakkam ma, neenga eppadi irukeenga? Unga EMI payment pending iruku.'"
            if language == "Tamil"
            else
            "Transcribe in Hinglish (Hindi words written in English letters). "
            "Example: 'Namaste ji, aapka EMI payment pending hai. Aaj payment kar sakte hain?'"
        )

        with open(tmp_path, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                file=(tmp_path, audio_file.read()),
                model="whisper-large-v3",
                language=lang_code,
                response_format="text",
                prompt=romanize_hint,
            )

        transcript = (
            transcription.strip()
            if isinstance(transcription, str)
            else transcription.text.strip()
        )

        if not transcript:
            raise RuntimeError("Groq returned empty transcript")

        # If native script still present, transliterate via Gemini
        if _has_native_script(transcript):
            transcript = _transliterate_to_roman(transcript, language)

        return transcript

    except Exception as e:
        raise RuntimeError(f"Transcription failed: {str(e)}")
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)