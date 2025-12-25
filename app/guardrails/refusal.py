from typing import List, Dict

MIN_CONFIDENCE = 0.4
MIN_SIMILARITY = 0.4

def should_refuse(
    confidence: float,
    retrieved_chunks: List[tuple]) -> bool:

    if not retrieved_chunks:
        return True

    # Low overall confidence
    if confidence < MIN_CONFIDENCE:
        return True

    # No strong retrieval signal
    max_similarity = max(score for _, score, _ in retrieved_chunks)
    if max_similarity < MIN_SIMILARITY:
        return True

    return False
