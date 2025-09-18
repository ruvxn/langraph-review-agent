from typing import List
import json
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.chat_models import ChatOllama
from src.utils import RawReview, DetectedError

# labels for errors
TYPES = {"Crash","Billing","Auth","API","Performance","Docs","Permissions","Mobile","UI","Webhooks","Other"}

#system prompt
SYSTEM = """You are a precise QA assistant.
Task: Given a customer review, extract ZERO OR MORE concrete PRODUCT/SERVICE PROBLEMS
OR FEATURE/ENHANCEMENT REQUESTS.

Return ONLY valid JSON with this exact shape:
{"errors":[{"error_summary":"...", "error_type":["Crash","Billing","Auth","API","Performance","Docs","Permissions","Mobile","UI","Webhooks","Other"], "rationale":"..."}]}

Guidelines:
- error_summary <= 140 chars, actionable (what/where). For feature/enhancement requests, start with "Feature request:" or "Enhancement:" and name the request (e.g., "Feature request: dark mode").
- If no problem or request is present, return {"errors": []}.
- Use multiple error_type labels if appropriate; for feature requests, use ["Other"] unless clearly UI/Docs/etc.
- Output must be ONLY the JSON object (no prose).
"""

# few shot to guide the model
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

FEWSHOT_USER_2 = """Review:
```
Could you add support for bulk edit on tasks?
```
Return JSON only:"""

FEWSHOT_ASSISTANT_2 = """{
  "errors": [{
    "error_summary": "Feature request: bulk edit for tasks",
    "error_type": ["Other"],
    "rationale": "User explicitly asks to add bulk-edit capability."
  }]
}"""


def make_llm(ollama_model: str = "llama3.2:latest"):
    #force JSON output from Ollama
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

#keyword fallback to guarantees something for obvious cases
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

    #fallback if LLM returned nothing to the set keweords
    if not out:
        out = _fallback_detect(review.review)

    return out