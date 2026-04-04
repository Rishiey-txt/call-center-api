import json
import google.generativeai as genai
from groq import Groq
from config import settings


# --- Configure Gemini ---
genai.configure(api_key=settings.GEMINI_API_KEY)
gemini_model = genai.GenerativeModel("gemini-1.5-flash")

# --- Configure Groq ---
groq_client = Groq(api_key=settings.GROQ_API_KEY)


# --- Your SYSTEM PROMPT (keep yours if already defined) ---
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

adherenceStatus: "FOLLOWED" only when ALL 5 stages are true. Otherwise "NOT_FOLLOWED".
paymentPreference: Choose based on what the customer agreed to or showed intent toward.
rejectionReason: "NONE" if payment was agreed to. Otherwise pick the closest reason.
keywords: Must be substrings or direct derivations of words in the transcript. Do not invent keywords.
summary: Must be in English regardless of the transcript language.
"""



# --- Build messages ---
def build_messages(transcript: str):
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": transcript}
    ]


# --- Gemini ---
def analyze_with_gemini(messages):
    print("🚀 Trying Gemini...")

    # Gemini doesn't use chat format like OpenAI/Groq
    prompt = f"{SYSTEM_PROMPT}\n\nTranscript:\n{messages[1]['content']}"

    response = gemini_model.generate_content(prompt)

    return response.text


# --- Groq ---
def analyze_with_groq(messages):
    print("⚡ Falling back to Groq...")

    response = groq_client.chat.completions.create(
        model="llama3-70b-8192",
        messages=messages,
        temperature=0.3,
    )

    return response.choices[0].message.content


# --- Safe JSON parser ---
def safe_parse(text: str):
    try:
        return json.loads(text)
    except Exception:
        print("❌ JSON parse failed")
        return None


# --- Heuristic fallback ---
def heuristic_analysis():
    return {
        "summary": "Fallback summary",
        "sop_validation": {
            "greeting": False,
            "identification": False,
            "problemStatement": False,
            "solutionOffering": False,
            "closing": False,
            "complianceScore": 0.0,
            "adherenceStatus": "NOT_FOLLOWED",
            "explanation": "Fallback mode"
        },
        "analytics": {
            "paymentPreference": "NONE",
            "rejectionReason": "NONE",
            "sentiment": "Neutral"
        },
        "keywords": []
    }


# --- MAIN FUNCTION ---
def analyze_transcript(transcript: str, language: str):
    messages = build_messages(transcript)

    # 1️⃣ Gemini
    try:
        result = analyze_with_gemini(messages)
        parsed = safe_parse(result)
        if parsed:
            return parsed
    except Exception as e:
        print("❌ Gemini failed:", e)

    # 2️⃣ Groq fallback
    try:
        result = analyze_with_groq(messages)
        parsed = safe_parse(result)
        if parsed:
            return parsed
    except Exception as e:
        print("❌ Groq failed:", e)

    # 3️⃣ Final fallback
    print("🪫 Using heuristic fallback")
    return heuristic_analysis()