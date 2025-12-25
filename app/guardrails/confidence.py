# app/guardrails/confidence.py

from typing import List, Dict
import re

REFUSAL_PATTERNS = [
    "i do not have enough information",
    "not provided in the context",
    "cannot be determined from the context",
    "no information is available",
]

def is_refusal(answer_text: str) -> bool:
    answer_lower = answer_text.lower()
    return any(p in answer_lower for p in REFUSAL_PATTERNS)


def estimate_confidence(
    retrieved_chunks: List[tuple],
    answer_text: str
) -> float:
    """
    Estimate confidence ∈ [0, 1] based on retrieval + answer quality.
    """

    if not retrieved_chunks or not answer_text: # in the case where there is no retrieval
        return 0.0
    
    if is_refusal(answer_text): # in the case where there is explicit refusal from the LLM
        return 0.0

    # 1. Retrieval coverage
    k = len(retrieved_chunks)
    coverage_score = min(k / 3, 1.0)  # saturates at 3 chunks

    # 2. Similarity strength
    scores = [score for _, score, _ in retrieved_chunks]
    avg_similarity = sum(scores) / len(scores)

    # Normalize assuming cosine similarity ~ [0.3, 0.8]
    similarity_score = min(max((avg_similarity - 0.3) / 0.5, 0), 1)

    # 3. Answer vs context length
    context_len = sum(len(chunk) for chunk, _, _ in retrieved_chunks)
    answer_len = len(answer_text)

    # Penalize overly long answers
    length_ratio = answer_len / max(context_len, 1)
    length_score = 1.0 if length_ratio <= 0.5 else max(0, 1 - (length_ratio - 0.5))

    # 4. Citation usage
    citations = re.findall(r"\[ID:.*?\]", answer_text)
    citation_score = min(len(citations) / k, 1.0)

    # Weighted combination
    confidence = (
        0.30 * coverage_score +
        0.30 * similarity_score +
        0.20 * length_score +
        0.20 * citation_score
    )

    return round(confidence, 3)
