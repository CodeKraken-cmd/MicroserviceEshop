import os, datetime, uuid
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Literal
from sqlalchemy import Column, String, Integer, Boolean, DateTime
from sqlalchemy.orm import declarative_base, Session, sessionmaker
from sqlalchemy import create_engine

DB_URL = os.getenv("LISTINGS_DB_URL", "sqlite:///./listings.db")
CORS = os.getenv("CORS_ORIGINS","http://localhost:5173,http://localhost:5174").split(",")

engine = create_engine(DB_URL, pool_pre_ping=True, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
Base = declarative_base()

class OfferModel(Base):
    __tablename__ = "offers"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    product_id = Column(String, index=True, nullable=False)
    seller_id = Column(String, nullable=False)
    price_cents = Column(Integer, nullable=False, default=0)
    condition = Column(String, default="new")
    rating_pct = Column(Integer, default=0)
    in_stock = Column(Boolean, default=True)
    is_prime_eligible = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Listings Service (DB)")
app.add_middleware(CORSMiddleware, allow_origins=CORS, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

class Offer(BaseModel):
    id: str | None = None
    product_id: str
    seller_id: str
    price_cents: int
    condition: Literal["new","used","refurbished"]="new"
    rating_pct: int | None = 0
    in_stock: bool = True
    is_prime_eligible: bool = False

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/products/{pid}/offers", response_model=List[Offer])
def list_offers(pid: str, db: Session = Depends(get_db)):
    rows = db.query(OfferModel).filter(OfferModel.product_id==pid, OfferModel.in_stock==True).all()
    rows.sort(key=lambda o: (o.price_cents, -(1 if o.is_prime_eligible else 0), - (o.rating_pct or 0)))
    return [Offer(**{k:getattr(r,k) for k in Offer.model_fields}) for r in rows]

@app.get("/products/{pid}/buybox", response_model=Offer)
def buybox(pid: str, db: Session = Depends(get_db)):
    items = list_offers(pid, db)
    if not items: raise HTTPException(404, "No offers")
    return items[0]

@app.post("/admin/offers", response_model=Offer)
def upsert_offer(o: Offer, db: Session = Depends(get_db)):
    if o.id:
        row = db.query(OfferModel).get(o.id)
        if not row: raise HTTPException(404, "Not found")
        for k,v in o.model_dump().items():
            if k=="id": continue
            setattr(row, k, v)
    else:
        row = OfferModel(**o.model_dump(exclude={"id"}))
        db.add(row)
    db.commit(); db.refresh(row)
    o.id = row.id
    return o

@app.get("/healthz")
def healthz(): return {"ok": True}
