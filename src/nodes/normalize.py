# src/nodes/normalize.py
from typing import List, Dict
from src.utils import RawReview, DetectedError, EnrichedError, hash_error
from src.nodes.classify_criticality import classify_criticality

def normalize(review: RawReview, detected: List[DetectedError]) -> List[EnrichedError]:
    enriched: List[EnrichedError] = []
    for e in detected:
        crit = classify_criticality(e)
        enriched.append(
            EnrichedError(
                review=review,
                error=e,
                criticality=crit,
                error_hash=hash_error(review.review_id, e.error_summary),
            )
        )

    # De-dupe within the review by error_hash
    uniq: Dict[str, EnrichedError] = {}
    for it in enriched:
        uniq[it.error_hash] = it
    return list(uniq.values())
