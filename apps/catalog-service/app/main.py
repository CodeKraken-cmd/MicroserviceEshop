import os, uuid, datetime
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import declarative_base, Session
from sqlalchemy import Column, String, Integer, DateTime
from libs_common.db import get_sessionmaker, session_dep, init_engine
from libs_common.auth_mw import jwt_user

DB_URL = os.getenv("CATALOG_DB_URL", "sqlite:///./catalog.db")
CORS = os.getenv("CORS_ORIGINS","http://localhost:5173,http://localhost:5174").split(",")

Base = declarative_base()
engine = init_engine(DB_URL)
SessionLocal = get_sessionmaker(DB_URL)
dep_session = session_dep(SessionLocal)

class Product(Base):
    __tablename__ = "products"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    sku = Column(String, unique=True, index=True, nullable=False)
    price_cents = Column(Integer, nullable=False, default=0)
    stock = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

Base.metadata.create_all(bind=engine)

class ProductIn(BaseModel):
    name: str
    sku: str
    price_cents: int
    stock: int = 0

app = FastAPI(title="Catalog Service")
app.add_middleware(CORSMiddleware, allow_origins=CORS, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.get("/products")
def list_products(db: Session = Depends(dep_session)):
    items = db.query(Product).order_by(Product.created_at.desc()).all()
    return {"items": [ {"id": p.id, "name": p.name, "sku": p.sku, "price_cents": p.price_cents, "stock": p.stock} for p in items ]}

@app.get("/products/{pid}")
def get_product(pid: str, db: Session = Depends(dep_session)):
    p = db.query(Product).get(pid)
    if not p: raise HTTPException(404, "Not found")
    return {"id": p.id, "name": p.name, "sku": p.sku, "price_cents": p.price_cents, "stock": p.stock}

@app.post("/admin/products")
def create_product(body: ProductIn, user=Depends(jwt_user), db: Session = Depends(dep_session)):
    # require admin role (simplified)
    if "admin" not in user.get("roles", []):
        raise HTTPException(403, "Admin only")
    p = Product(name=body.name, sku=body.sku, price_cents=body.price_cents, stock=body.stock)
    db.add(p); db.commit(); db.refresh(p)
    return {"id": p.id, "name": p.name, "sku": p.sku, "price_cents": p.price_cents, "stock": p.stock}

@app.put("/admin/products/{pid}")
def update_product(pid: str, body: ProductIn, user=Depends(jwt_user), db: Session = Depends(dep_session)):
    if "admin" not in user.get("roles", []):
        raise HTTPException(403, "Admin only")
    p = db.query(Product).get(pid)
    if not p: raise HTTPException(404, "Not found")
    p.name, p.sku, p.price_cents, p.stock = body.name, body.sku, body.price_cents, body.stock
    db.commit(); db.refresh(p)
    return {"id": p.id, "name": p.name, "sku": p.sku, "price_cents": p.price_cents, "stock": p.stock}

@app.get("/healthz")
def healthz(): return {"ok": True}
