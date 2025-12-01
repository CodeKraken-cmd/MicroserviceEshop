from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import os

CORS = os.getenv("CORS_ORIGINS","http://localhost:5173,http://localhost:5174").split(",")
app = FastAPI(title="Reviews Service")
app.add_middleware(CORSMiddleware, allow_origins=CORS, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

class Review(BaseModel):
    id: str
    product_id: str
    user_id: str
    rating: int
    text: str
    verified_purchase: bool = False

REVIEWS: dict[str, Review] = {}

@app.post("/reviews", response_model=Review)
def create(r: Review):
    REVIEWS[r.id] = r; return r

@app.get("/products/{pid}/reviews", response_model=List[Review])
def list_for_product(pid: str):
    return [r for r in REVIEWS.values() if r.product_id == pid]

@app.get("/products/{pid}/review-highlight")
def highlight(pid: str):
    texts = [r.text for r in REVIEWS.values() if r.product_id == pid and r.verified_purchase]
    if not texts: raise HTTPException(404, "No verified reviews")
    snippet = texts[0][:240]
    return {"highlight": snippet, "verified_only": True}

@app.get("/healthz")
def healthz(): return {"ok": True}
