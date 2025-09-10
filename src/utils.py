from pydantic import BaseModel, Field
from typing import List, Literal
import hashlib

Criticality = Literal["Critical", "Major", "Minor", "Suggestion", "None"]

class RawReview(BaseModel):
    review_id: str
    review: str
    username: str
    email: str
    date: str
    reviewer_name: str
    rating: int

class DetectedError(BaseModel):
    error_summary: str
    error_type: List[str] = Field(default_factory=list)
    rationale: str

class EnrichedError(BaseModel):
    review: RawReview
    error: DetectedError
    criticality: Criticality
    error_hash: str

def hash_error(review_id: str, summary: str) -> str:
    key = f"{review_id}|{summary}".encode("utf-8")
    return hashlib.sha256(key).hexdigest()[:16]
