# src/nodes/detect_errors.py
from typing import List
import json
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.chat_models import ChatOllama
from src.utils import RawReview, DetectedError

# --- Config ---
TYPES = {"Crash","Billing","Auth","API","Performance","Docs","Permissions","Mobile","UI","Webhooks","Other"}

SYSTEM = """You are a precise QA assistant.
Task: Given a customer review, extract ZERO OR MORE concrete PRODUCT/SERVICE PROBLEMS.

Return ONLY valid JSON with this exact shape:
{"errors":[{"error_summary":"...", "error_type":["Crash","Billing","Auth","API","Performance","Docs","Permissions","Mobile","UI","Webhooks","Other"], "rationale":"..."}]}

Guidelines:
- error_summary <= 140 chars, actionable (what/where).
- If no real problem is present, return {"errors": []}.
- Prefer specific types; include multiple types if appropriate.
- Output must be ONLY the JSON object (no prose).
"""

# Tiny few-shot to steer the model
FEWSHOT_USER = """Review:
```
Not thrilled about how the mobile app crashes whenever I switch workspaces. Lost my draft twice.
```
Return JSON only:"""
FEWSHOT_ASSISTANT = """{"errors":[{"error_summary":"Mobile app crashes when switching workspaces","error_type":["Mobile","Crash"],"rationale":"User reports reproducible crash and data loss while switching workspaces."}]}"""

USER = """Review:
```
{review_text}
```
Return JSON only:"""

def make_llm(ollama_model: str = "llama3.2:latest"):
    # Force JSON output from Ollama
    return ChatOllama(model=ollama_model, temperature=0, format="json")

def _json_load(s: str) -> dict:
    if not s:
        return {"errors": []}
    s = s.strip()
    try:
        return json.loads(s)
    except Exception:
        a, b = s.find("{"), s.rfind("}")
        if a != -1 and b != -1 and b > a:
            try:
                return json.loads(s[a:b+1])
            except Exception:
                return {"errors": []}
        return {"errors": []}

# --- Keyword fallback (guarantees something for obvious cases) ---
FALLBACK_RULES = [
    ("Mobile app crashes when switching workspaces", ["Mobile","Crash"],
     ["crash", "crashes", "crashing", "workspace"]),
    ("Invoice total mismatches usage/billing metrics", ["Billing"],
     ["invoice", "overcharged", "duplicate charge", "billing mismatch", "billing error"]),
    ("Authentication/session expires unexpectedly", ["Auth"],
     ["auth", "authentication", "session expires", "token expires", "login fails", "cannot login", "can't login"]),
    ("API requests time out or are very slow", ["API","Performance"],
     ["timeout", "time out", "very slow", "slow request", "latency", "rate limit"]),
    ("Webhooks deliver duplicates or invalid signatures", ["Webhooks"],
     ["webhook", "duplicate event", "signature fail", "signature verification"]),
    ("Docs are outdated or inconsistent", ["Docs"],
     ["docs outdated", "documentation outdated", "example wrong", "missing example"]),
    ("UI layout shifts or elements off-canvas", ["UI"],
     ["layout shift", "off-canvas", "alignment", "button missing", "overlapping"]),
]

def _fallback_detect(text: str) -> List[DetectedError]:
    s = text.lower()
    out: List[DetectedError] = []
    for summary, types, kws in FALLBACK_RULES:
        if any(k in s for k in kws):
            out.append(DetectedError(
                error_summary=summary[:140],
                error_type=types,
                rationale="Keyword-based heuristic match from review text."
            ))
    return out

def detect_errors_with_ollama(
    review: RawReview,
    ollama_model: str = "llama3.2:latest",
) -> List[DetectedError]:
    llm = make_llm(ollama_model)
    
    # Build the full prompt manually to avoid ChatPromptTemplate issues
    full_prompt = f"""{SYSTEM}

{FEWSHOT_USER}

{FEWSHOT_ASSISTANT}

Review:
```
{review.review[:4000]}
```
Return JSON only:"""
    
    resp = llm.invoke(full_prompt)

    raw = (getattr(resp, "content", "") or "").strip()
    data = _json_load(raw)
    items = data.get("errors", [])
    out: List[DetectedError] = []

    if isinstance(items, list):
        for e in items:
            if not isinstance(e, dict):
                continue
            summary = (e.get("error_summary") or "").strip()[:140]
            types = e.get("error_type") or []
            if isinstance(types, str):
                types = [types]
            types = [t for t in types if isinstance(t, str) and t in TYPES] or ["Other"]
            rationale = (e.get("rationale") or "").strip()
            if summary:
                out.append(DetectedError(
                    error_summary=summary,
                    error_type=types,
                    rationale=rationale
                ))

    # Fallback if LLM returned nothing
    if not out:
        out = _fallback_detect(review.review)

    return out