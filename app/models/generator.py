import os
import time
from typing import List, Tuple, Dict
from dotenv import load_dotenv
import logging
import requests

# Setup
logger = logging.getLogger("uvicorn.error")
load_dotenv()

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "mistral:7b-instruct"

def generate_answer(
    query: str, 
    retrieved_chunks: List[Tuple[str, float, Dict]], 
    model_tier: str = OLLAMA_MODEL) -> Dict:
    
    if not retrieved_chunks:
        return {
            "answer": None,
            "sources": [],
            "model_used": model_tier,
            "latency": 0,
            "reason": "No retrieved context"
        }
    
    start_time = time.time()
    
    # Prepare Context and Citations
    context_blocks = []
    sources = []

    for chunk, score, meta in retrieved_chunks:
        cid = meta.get("chunk_id", "Unknown")
        context_blocks.append(f"[ID: {cid}]\n{chunk}")
        sources.append({"id": cid, "source": meta.get("source"), "score": score})

    context_text = "\n\n".join(context_blocks)

    # Construct Prompt with strict grounding
    prompt = f"""
    Instructions:
    - You are an AI assistant. 
    - Answer the question using ONLY the provided context.
    - Do NOT use any prior knowledge.
    - If the answer is not in the context, state that you do not have enough information.
    - Answer ONLY what is necessary to directly answer the question.
    - Do not include additional policy information unless it is explicitly required.
    - After any sentence that comes from a specific chunk, include a citation like [ID: chunk_id].
    - If multiple chunks support the same point, cite all relevant IDs, e.g., [ID: chunk1, chunk2].
    - Do NOT fabricate information or make assumptions.
    - If the context does not provide the answer, say exactly: "I do not have enough information in the provided context."

    CONTEXT:
    {context_text}

    QUESTION: 
    {query}
    """

    # Call LLM
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": model_tier,
                "prompt": prompt,
                "stream": False
            },
            timeout=60
        )

        response.raise_for_status()
        answer_text = response.json()["response"].strip()

        if not answer_text:
            answer_text = "I do not have enough information in the provided context."

    except Exception as e:
        logger.error(f"Ollama error: {e}")
        return {
            "answer": None,
            "sources": sources,
            "model_used": model_tier,
            "latency": round(time.time() - start_time, 3),
            "reason": f"LLM error: {str(e)}"
        }
    
    latency = round(time.time() - start_time, 3)

    # Return the structured data
    return {
        "answer": answer_text,
        "sources": sources,
        "model_used": model_tier,
        "latency": latency
    }