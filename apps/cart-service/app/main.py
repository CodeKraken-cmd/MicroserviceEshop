import os, json
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from libs_common.auth_mw import jwt_user
import redis

CORS = os.getenv("CORS_ORIGINS","http://localhost:5173,http://localhost:5174").split(",")
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
r = redis.from_url(REDIS_URL, decode_responses=True)

class CartItem(BaseModel):
    product_id: str
    offer_id: str | None = None
    qty: int = 1
    unit_price_cents: int = 0

app = FastAPI(title="Cart Service")
app.add_middleware(CORSMiddleware, allow_origins=CORS, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

def _key(uid): return f"cart:{uid}"

@app.get("/items")
def items(user=Depends(jwt_user)):
    raw = r.get(_key(user["sub"])) or json.dumps({"items": []})
    return json.loads(raw)

@app.post("/add")
def add(item: CartItem, user=Depends(jwt_user)):
    cart = items(user)
    cart["items"].append(item.dict())
    r.set(_key(user["sub"]), json.dumps(cart))
    return cart

@app.delete("/clear")
def clear(user=Depends(jwt_user)):
    r.delete(_key(user["sub"])); return {"ok": True}

@app.get("/healthz")
def healthz(): return {"ok": True}
