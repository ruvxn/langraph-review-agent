# src/nodes/classify_criticality.py
from typing import List
from src.utils import DetectedError, Criticality

# Keyword buckets (tune anytime)
BUCKETS: dict[Criticality, List[str]] = {
    "Critical": [
        "crash", "crashes", "crashing",
        "data loss", "lost data",
        "fails to login", "cannot login", "can't login", "login failure",
        "payment fails", "charge failed", "payment error",
        "outage", "downtime", "service down", "unavailable",
        "security breach", "leak", "p0",
    ],
    "Major": [
        "timeout", "very slow", "slow query", "latency",
        "duplicate charge", "overcharged", "billing mismatch",
        "token expires", "auth expires", "session expires",
        "inconsistent api", "breaking change", "backward incompatible",
        "webhook duplicate", "retry storm",
        "memory leak", "high cpu", "high cpu usage",
    ],
    "Minor": [
        "typo", "grammar", "layout shift", "overlapping",
        "button off-canvas", "alignment", "color contrast",
        "docs outdated", "example wrong", "missing example",
    ],
    "Suggestion": [
        "wish", "would be nice", "feature request",
        "could you add", "please add", "it would help if",
    ],
    "None": [],
}

def classify_criticality(err: DetectedError) -> Criticality:
    s = f"{err.error_summary} {' '.join(err.error_type)}".lower()

    # Priority order matters
    for level in ("Critical", "Major", "Minor", "Suggestion"):
        for kw in BUCKETS[level]:  # type: ignore[index]
            if kw in s:
                return level  # type: ignore[return-value]

    # Type-based fallbacks (helps even if no keywords)
    if "Crash" in err.error_type or "Billing" in err.error_type and "duplicate" in s:
        return "Critical"
    if "Performance" in err.error_type or "Auth" in err.error_type or "API" in err.error_type:
        return "Major"
    if "UI" in err.error_type or "Docs" in err.error_type:
        return "Minor"

    return "None"
