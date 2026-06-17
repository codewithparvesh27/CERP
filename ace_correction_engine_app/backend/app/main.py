from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from app.api.sessions import router as sessions_router

app = FastAPI(title="ACE Correction Engine", version="0.1.0")
origins = [o.strip() for o in os.getenv("BACKEND_CORS_ORIGINS", "http://localhost:5173").split(",")]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(sessions_router, prefix="/api")

@app.get("/health")
def health():
    return {"status": "ok"}
