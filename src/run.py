# src/run.py
from src.graph import build_graph

if __name__ == "__main__":
    wf = build_graph().compile()
    enriched = wf.invoke({})

    print(f"\n Done. Processed {len(enriched)} enriched errors.\n")

    for idx, e in enumerate(enriched[:20], start=1):  # show first 20 for readability
        print("─" * 60)
        print(f"Review #{idx} ({e.review.review_id}, rating={e.review.rating})")
        print(f"Text: {e.review.review[:250]}")  # truncate long text
        print()
        print(f"→ Severity: {e.criticality}")
        print(f"→ Categories: {e.error.error_type}")
        print(f"→ Summary: {e.error.error_summary}")
        print(f"→ Rationale: {e.error.rationale}")
        print()
