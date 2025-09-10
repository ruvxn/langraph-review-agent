# tests/smoke.py
from src.config import DATA_PATH, OLLAMA_MODEL
from src.nodes.load_reviews import load_reviews
from src.nodes.detect_errors import detect_errors_with_ollama
from src.nodes.normalize import normalize

if __name__ == "__main__":
    reviews = load_reviews(DATA_PATH)
    print(f"Loaded {len(reviews)} reviews")

    for i, r in enumerate(reviews[:3], start=1):
        errs = detect_errors_with_ollama(r, OLLAMA_MODEL)
        enriched = normalize(r, errs)

        print(f"\nReview #{i} | id={r.review_id} | rating={r.rating}")
        print(r.review[:220] + ("..." if len(r.review) > 220 else ""))

        if not enriched:
            print("→ No errors detected.")
        else:
            for e in enriched:
                print(f"→ [{e.criticality}] {e.error.error_summary} | types={e.error.error_type} | hash={e.error_hash}")
