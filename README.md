(refer to the VerifAI.pdf for the full documentation of this project)

# VerifAI

A refusal-aware RAG system for proprietary documents that prioritizes grounding, confidence estimation, and observability over answer rate

## Project Overview

VerifAI is a Retrieval-Augmented Generation (RAG) system designed specifically for proprietary and internal knowledge bases, such as company policies, onboarding documents, and internal manuals.

Unlike general-purpose chatbots that optimize for answer rate or conversational fluency, VerifAI is built around correctness-first principles. It explicitly refuses to answer when insufficient evidence exists, quantifies answer confidence using observable signals, and exposes full system behavior through structured logging and monitoring.

This makes VerifAI suitable for enterprise, compliance-sensitive, and internal AI deployments where hallucinations are unacceptable and traceability is required.

## Document Set (Knowledge Base)

This system ingests policy documents that have been generated with use of Gemini to mimic intern onboarding documents covering:

1. Intern_Confidentiality_and_Acceptable_Use_Policy
2. Intern_Data_Privacy_Notice
3. Intern_Inventions_and_IP_Policy
4. New_Joiner_Internship_Handbook

These documents form the source text used for retrieval.

## Repository Structure

- prodguard/
  - app/
    - main.py # FastAPI entrypoint
    - api/
      - query.py
    - guardrails/ # Confidence & refusal logic
      - confidency.py
      - refusal.py
    - logging/
      - structured_logger.py
    - models/
      - generator.py
    - retreival/
      - retriever.py
  - chroma_db
  - dashboard/
    - dashboard.py
  - data/
    - chunks/ # Chunked Docs in json
    - evaluation/ # input json file for evaluation script
    - raw/ # Raw policy docs
    - processed/ # Cleaned docs
  - scripts/ # Data processing scripts
  - README.md
  - requirements.txt

## Running the Application

1. Install Dependencies

```
pip install fastapi uvicorn chromadb sentence-transformers streamlit pandas
```

2. Install Ollama LLM locally

```
brew install ollama
```

3. Starting Ollama service

```
ollama serve
```

4. Start the API server

```
uvicorn app.main:app --reload
```

5. Verify that the server is running

```
curl http://localhost:8000/health
```

The expected response is { "status": "ok" }

6. Querying the system

```
curl -X POST http://127.0.0.1:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What are my rights regarding personal projects?"}'
```

Example response of an answer being returned

```
{"answer":"Based on the provided context, if your personal project was created entirely on your own time, using no Company resources (including laptops or proprietary data), and does not compete with the Company’s business interests [ID: Intern_Inventions_and_IP_Policy_4], then it is considered personal property. However, if the project is created during the internship period or uses company resources, it becomes the exclusive property of the Company [ID: New_Joiner_Internship_Handbook_7, ID: Intern_Confidentiality_and_Acceptable_Use_Policy_5]. Therefore, I would suggest you clarify these conditions with your employer to ensure your personal projects are not inadvertently compromised.","sources":[{"id":"Intern_Inventions_and_IP_Policy_4","source":"Intern_Inventions_and_IP_Policy.txt","score":0.555810018319265},{"id":"New_Joiner_Internship_Handbook_7","source":"New_Joiner_Internship_Handbook.txt","score":0.49159465133621366},{"id":"Intern_Confidentiality_and_Acceptable_Use_Policy_5","source":"Intern_Confidentiality_and_Acceptable_Use_Policy.txt","score":0.4887695448491631}],"model_used":"mistral:7b-instruct","confidence":0.757,"latency":5664}
```

Exmaple of a refusal as a response

```
{"answer":null,"reason":"INSUFFICIENT_POLICY_GROUNDING","sources":[{"id":"New_Joiner_Internship_Handbook_3","source":"New_Joiner_Internship_Handbook.txt","score":0.3662955652978883},{"id":"Intern_Inventions_and_IP_Policy_2","source":"Intern_Inventions_and_IP_Policy.txt","score":0.3642010261319175},{"id":"Intern_Inventions_and_IP_Policy_7","source":"Intern_Inventions_and_IP_Policy.txt","score":0.36344169765748735}],"model_used":"mistral:7b-instruct","confidence":null,"latency":3691}
```

7. Running the dashboard

```
streamlit run dashboard/dashboard.py
```
