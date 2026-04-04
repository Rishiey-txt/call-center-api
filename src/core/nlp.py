import google.generativeai as genai
import json
from src.config import settings

genai.configure(api_key=settings.GEMINI_API_KEY)

SYSTEM_PROMPT = """
You are a call center compliance analyzer for an Indian education institution.
Given a transcript of a customer service call, return ONLY valid JSON with this exact structure. No markdown. No explanation.

{
  "summary": "2-3 sentence summary of the call in English",
  "sop": {
    "greeting": true or false,
    "identification": true or false,
    "problemStatement": true or false,
    "solutionOffering": true or false,
    "closing": true or false,
    "explanation": "one sentence explaining what was missing or why it is compliant"
  },
  "paymentPreference": "EMI" or "FULL_PAYMENT" or "PARTIAL_PAYMENT" or "DOWN_PAYMENT",
  "rejectionReason": "HIGH_INTEREST" or "BUDGET_CONSTRAINTS" or "ALREADY_PAID" or "NOT_INTERESTED" or "NONE",
  "sentiment": "Positive" or "Negative" or "Neutral",
  "keywords": ["8 to 12 keywords directly from the transcript"]
}

SOP stage definitions:
- greeting: Agent opened with a salutation (Hello, Vanakkam, Namaste, Hi)
- identification: Agent explicitly verified customer name or account (NOT just calling them by name — must confirm)
- problemStatement: Agent explained the purpose of the call clearly (outstanding dues, course inquiry, etc.)
- solutionOffering: Agent proposed a specific solution (EMI plan, course details, discount, payment option)
- closing: Agent ended with thank you / goodbye / next-step commitment
"""

def analyze_transcript(transcript: str, language: str) -> dict:
    try:
        model = genai.GenerativeModel(
            model_name="models/gemini-2.0-flash",
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                temperature=0.1,
            ),
            system_instruction=SYSTEM_PROMPT,
        )
        response = model.generate_content(
            f"Language: {language}\n\nTranscript:\n{transcript}"
        )
        return json.loads(response.text)
    except Exception as e:
        raise RuntimeError(f"NLP analysis via Gemini failed: {str(e)}")
