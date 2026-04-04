from pydantic import BaseModel
from typing import Literal

class CallAnalyticsRequest(BaseModel):
    language: Literal["Tamil", "Hindi"]
    audioFormat: Literal["mp3"]
    audioBase64: str   # Base64-encoded MP3 bytes
