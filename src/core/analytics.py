VALID_PAYMENT = {"EMI", "FULL_PAYMENT", "PARTIAL_PAYMENT", "DOWN_PAYMENT"}
VALID_REJECTION = {"HIGH_INTEREST", "BUDGET_CONSTRAINTS", "ALREADY_PAID", "NOT_INTERESTED", "NONE"}
VALID_SENTIMENT = {"Positive", "Negative", "Neutral"}

def safe_payment(val: str) -> str:
    return val if val in VALID_PAYMENT else "FULL_PAYMENT"

def safe_rejection(val: str) -> str:
    return val if val in VALID_REJECTION else "NONE"

def safe_sentiment(val: str) -> str:
    # normalize capitalization
    normalized = val.capitalize() if val else "Neutral"
    return normalized if normalized in VALID_SENTIMENT else "Neutral"
