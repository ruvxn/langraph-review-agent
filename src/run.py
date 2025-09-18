from src.graph import wf

if __name__ == "__main__":
    enriched = wf.invoke({})  
    print(f"\n Done. Processed {len(enriched)} enriched errors.\n")
    print("────────────────────────────────────────────────────────────")

    for idx, e in enumerate(enriched, 1):
        # extra safety in case something upstream changes
        if not hasattr(e, "review"):
            continue
        print(f"Review #{idx} ({e.review.review_id}, rating={e.review.rating})")
        print(f"Text: {e.review.review}")
        print(f" → Severity: {e.criticality}")
        print(f" → Categories: {e.error.error_type}")
        print(f" → Summary: {e.error.error_summary}")
        print(f" → Rationale: {e.error.rationale}")
        print()
