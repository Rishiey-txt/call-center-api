def validate_keywords(keywords: list[str], transcript: str, summary: str) -> list[str]:
    """
    Filters LLM-generated keywords to only those actually present
    in or directly derivable from the transcript/summary.
    Ensures at least 5 keywords are returned.
    """
    source = (transcript + " " + summary).lower()
    valid = []
    for kw in keywords:
        if kw.lower() in source or any(word in source for word in kw.lower().split()):
            valid.append(kw)

    # fallback: extract nouns if too few valid keywords
    if len(valid) < 5:
        fallback = extract_fallback_keywords(transcript, summary)
        valid.extend(fallback)
        valid = list(dict.fromkeys(valid))

    return valid[:12]   # cap at 12

def extract_fallback_keywords(transcript: str, summary: str) -> list[str]:
    """
    Simple noun-phrase extractor using word frequency as fallback.
    """
    import re
    from collections import Counter

    stop = {"the","a","an","is","are","was","to","of","and","in","for","on","that",
            "this","it","be","with","at","by","i","you","he","she","we","they",
            "my","your","our","me","him","her","us","them"}

    text = (transcript + " " + summary).lower()
    words = re.findall(r"[a-zA-Z]{4,}", text)
    freq = Counter(w for w in words if w not in stop)
    return [w.title() for w, _ in freq.most_common(10)]
