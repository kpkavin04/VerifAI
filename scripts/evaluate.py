import json
import csv
import requests
import time

API_URL = "http://127.0.0.1:8000/query"

with open("data/evaluation/evaluation.json") as f:
    cases = json.load(f)

results = []

for case in cases:
    start = time.time()
    resp = requests.post(API_URL, json={"question": case["question"]})
    data = resp.json()
    latency = time.time() - start

    answer = data.get("answer")
    sources = data.get("sources", [])
    confidence = data.get("confidence", 0)

    grounded = all(
        any(src["id"].startswith(exp) for exp in case["expected_sources"])
        for src in sources
    ) if case["expected_sources"] else True

    faithful = not (answer is not None and case["acceptable_refusal"])
    refusal_correct = (
        answer is None if case["acceptable_refusal"] else answer is not None
    )

    results.append({
        "id": case["id"],
        "grounded": grounded,
        "faithful": faithful,
        "refusal_correct": refusal_correct,
        "confidence": confidence,
        "latency": round(latency, 3),
        "answered": answer is not None
    })

with open("evaluation_results.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=results[0].keys())
    writer.writeheader()
    writer.writerows(results)

print("Evaluation complete. Saved to evaluation_results.csv")
