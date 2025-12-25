from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import time
from app.retrieval.retriever import Retriever
from app.models.generator import generate_answer
from app.guardrails.confidence import estimate_confidence
from app.guardrails.refusal import should_refuse
from app.logging.structured_logger import log_request
import logging
logger = logging.getLogger("")


router = APIRouter()

# retriever
retriever = Retriever()

class QueryRequest(BaseModel):
    question: str
    top_k: int = 3

@router.post("/query")
def query_rag(request: QueryRequest):

    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    # retrieval
    retrieval_start = time.time()
    try:
        retrieved_chunks = retriever.retrieve(
            query=request.question,
            top_k=request.top_k
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Retrieval error: {str(e)}")
    retrieval_latency = round((time.time() - retrieval_start)*1000)

    # generation
    generation_start = time.time()
    result = generate_answer(
        query=request.question,
        retrieved_chunks=retrieved_chunks
    )
    generation_latency = round((time.time() - generation_start)*1000)

    # Add total latency (retrieval latency + generation latency)
    total_latency = retrieval_latency + generation_latency

    confidence = estimate_confidence(retrieved_chunks, result["answer"])

    refused = should_refuse(confidence, retrieved_chunks)

    if refused:
        outcome = "REFUSED_NO_STRONG_RETRIEVAL"
        refusal_reason = "INSUFFICIENT_POLICY_GROUNDING"
    else:
        outcome = "ANSWERED"
        refusal_reason = None

    log_request({
        "query": request.question,
        "retrieval": {
            "top_k": request.top_k,
            "retrieved_docs": [
                {
                    "chunk_id": meta.get("chunk_id"),
                    "score": round(score, 3)
                }
                for _, score, meta in retrieved_chunks
            ]
        },
        "generation": {
            "model": result["model_used"],
            "answer": None if refused else result["answer"],
            "refusal_reason": refusal_reason
        },
        "confidence": None if refused else confidence,
        "latency_ms": {
            "retrieval": retrieval_latency,
            "generation": generation_latency,
            "total": total_latency
        },
        "cost": 0.0,
        "outcome": outcome
    })

    if refused:
        return {
            "answer": None,
            "reason": refusal_reason,
            "sources": result["sources"],
            "model_used": result["model_used"],
            "confidence": None,
            "latency": total_latency
        }

    return {
        "answer": result["answer"],
        "sources": result["sources"],
        "model_used": result["model_used"],
        "confidence": confidence,
        "latency": total_latency
    }