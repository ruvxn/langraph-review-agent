# src/graph.py
from typing import Any, List, Tuple
from langgraph.graph import Graph
from src.config import DATA_PATH, OLLAMA_MODEL
from src.nodes.load_reviews import load_reviews
from src.nodes.detect_errors import detect_errors_with_ollama
from src.nodes.normalize import normalize
from src.utils import RawReview, DetectedError, EnrichedError

def build_graph() -> Graph:
    g = Graph()

    # 1) Load all reviews (limit during dev if you want)
    def n_load(_: dict) -> List[RawReview]:
        data = load_reviews(DATA_PATH)
        return data[:50]  # comment to speed up while testing
        #return data

    # 2) Detect errors with Ollama (per review)
    def n_detect(reviews: List[RawReview]) -> List[Tuple[RawReview, List[DetectedError]]]:
        pairs: List[Tuple[RawReview, List[DetectedError]]] = []
        for r in reviews:
            errs = detect_errors_with_ollama(r, OLLAMA_MODEL)
            pairs.append((r, errs))
        return pairs

    # 3) Normalize + classify + hash (flatten)
    def n_normalize(pairs: List[Tuple[RawReview, List[DetectedError]]]) -> List[EnrichedError]:
        out: List[EnrichedError] = []
        for r, errs in pairs:
            out.extend(normalize(r, errs))
        return out

    # Nodes
    g.add_node("load", n_load)
    g.add_node("detect", n_detect)
    g.add_node("normalize", n_normalize)

    # Edges
    g.add_edge("load", "detect")
    g.add_edge("detect", "normalize")

    # Entry & finish
    g.set_entry_point("load")
    g.set_finish_point("normalize")

    return g
