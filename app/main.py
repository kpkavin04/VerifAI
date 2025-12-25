from fastapi import FastAPI
from app.api.query import router as query_router

app = FastAPI(title = 'VerifAI')

@app.get("/health")
def health_check():
    return {"status":"ok"}

app.include_router(query_router)