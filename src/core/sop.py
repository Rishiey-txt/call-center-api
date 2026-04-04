def compute_compliance_score(sop_bools: dict) -> float:
    """
    sop_bools: dict with keys greeting, identification, problemStatement,
               solutionOffering, closing — all bool
    Returns float 0.0–1.0
    """
    fields = ["greeting", "identification", "problemStatement", "solutionOffering", "closing"]
    true_count = sum(1 for f in fields if sop_bools.get(f, False))
    return round(true_count / 5.0, 1)

def determine_adherence(sop_bools: dict) -> str:
    fields = ["greeting", "identification", "problemStatement", "solutionOffering", "closing"]
    if all(sop_bools.get(f, False) for f in fields):
        return "FOLLOWED"
    return "NOT_FOLLOWED"

def heuristic_sop(transcript: str) -> dict:
    t = transcript.lower()

    greeting_words = ["hello", "hi ", "vanakkam", "namaste", "good morning", "good afternoon"]
    greeting = any(w in t for w in greeting_words)

    id_phrases = ["is this", "am i speaking", "can i confirm", "your name please", "verify"]
    identification = any(p in t for p in id_phrases)

    problem_words = ["outstanding", "emi", "due", "payment", "inquiry", "course", "calling from"]
    problem_statement = any(w in t for w in problem_words)

    solution_words = ["emi option", "installment", "plan", "discount", "offer", "we can", "i can help"]
    solution_offering = any(w in t for w in solution_words)

    closing_words = ["thank you", "thanks", "goodbye", "bye", "nandri", "take care", "have a nice"]
    closing = any(w in t for w in closing_words)

    bools = {
        "greeting": greeting,
        "identification": identification,
        "problemStatement": problem_statement,
        "solutionOffering": solution_offering,
        "closing": closing,
    }
    score = compute_compliance_score(bools)
    status = determine_adherence(bools)

    return {**bools, "complianceScore": score, "adherenceStatus": status,
            "explanation": "Heuristic analysis — LLM unavailable."}
