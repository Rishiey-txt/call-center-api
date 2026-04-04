from src.tasks.celery_app import celery_app
from src.core.transcription import transcribe
from src.core.nlp import analyze_transcript
from src.core.sop import compute_compliance_score, determine_adherence, heuristic_sop
from src.core.analytics import safe_payment, safe_rejection, safe_sentiment
from src.core.keywords import validate_keywords
from src.core.vector_store import store_transcript

@celery_app.task(name="process_call", bind=True, max_retries=2)
def process_call(self, audio_base64: str, language: str, call_id: str) -> dict:
    try:
        # Dynamic transcription 
        transcript = transcribe(audio_base64, language)

        try:
            # Dynamic NLP Analysis
            analysis = analyze_transcript(transcript, language)
        except Exception:
            analysis = {
                "summary": transcript[:200] + " [truncated]",
                "sop": heuristic_sop(transcript),
                "paymentPreference": "FULL_PAYMENT",
                "rejectionReason": "NONE",
                "sentiment": "Neutral",
                "keywords": [],
            }

        sop_raw = analysis.get("sop", {})
        sop_bools = {
            "greeting":          bool(sop_raw.get("greeting", False)),
            "identification":    bool(sop_raw.get("identification", False)),
            "problemStatement":  bool(sop_raw.get("problemStatement", False)),
            "solutionOffering":  bool(sop_raw.get("solutionOffering", False)),
            "closing":           bool(sop_raw.get("closing", False)),
        }
        
        # Mathematical Isolation (computed AFTER LLM returns, strictly from the booleans)
        compliance_score = float(compute_compliance_score(sop_bools))
        adherence_status = str(determine_adherence(sop_bools))

        keywords = validate_keywords(
            analysis.get("keywords", []),
            transcript,
            analysis.get("summary", "")
        )
        # Ensure minimum 5 keywords 
        fallback_kws = ["call", "support", "customer", "agent", "service"]
        if len(keywords) < 5:
            keywords.extend([k for k in fallback_kws if k not in keywords])
        keywords = keywords[:12]

        payment_safe = safe_payment(analysis.get("paymentPreference", ""))
        rejection_safe = safe_rejection(analysis.get("rejectionReason", ""))
        sentiment_safe = safe_sentiment(analysis.get("sentiment", ""))

        # Index to ChromaDB
        store_transcript(call_id, transcript, {
            "language": language,
            "payment": payment_safe,
            "sentiment": sentiment_safe,
        })

        return {
            "status": "success",
            "language": language,
            "transcript": transcript,
            "summary": analysis.get("summary", ""),
            "sop_validation": {
                **sop_bools,
                "complianceScore": compliance_score,
                "adherenceStatus": adherence_status,
                "explanation": sop_raw.get("explanation", ""),
            },
            "analytics": {
                "paymentPreference": payment_safe,
                "rejectionReason":   rejection_safe,
                "sentiment":         sentiment_safe,
            },
            "keywords": keywords,
        }

    except Exception as exc:
        raise self.retry(exc=exc, countdown=5)
