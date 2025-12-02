import os, datetime, uuid
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import Column, String, Integer, DateTime, Boolean
from sqlalchemy.orm import declarative_base, Session, sessionmaker
from sqlalchemy import create_engine

DB_URL = os.getenv("AUCTIONS_DB_URL","sqlite:///./auctions.db")
CORS = os.getenv("CORS_ORIGINS","http://localhost:5173,http://localhost:5174").split(",")

engine = create_engine(DB_URL, pool_pre_ping=True, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
Base = declarative_base()

class AuctionModel(Base):
    __tablename__ = "auctions"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    listing_id = Column(String, nullable=False)
    ends_at = Column(DateTime, nullable=False)
    reserve_cents = Column(Integer, nullable=True)
    bin_price_cents = Column(Integer, nullable=True)
    current_bid_cents = Column(Integer, default=0)
    high_bidder_id = Column(String, nullable=True)
    active = Column(Boolean, default=True)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Auctions Service (DB)")
app.add_middleware(CORSMiddleware, allow_origins=CORS, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

class Auction(BaseModel):
    id: str | None = None
    listing_id: str
    ends_at: datetime.datetime
    reserve_cents: int | None = None
    bin_price_cents: int | None = None
    current_bid_cents: int = 0
    high_bidder_id: str | None = None
    active: bool = True

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/admin/auctions", response_model=Auction)
def create_a(a: Auction, db: Session = Depends(get_db)):
    row = AuctionModel(**a.model_dump(exclude={"id"}))
    db.add(row); db.commit(); db.refresh(row)
    a.id = row.id; return a

@app.post("/auctions/{id}/bid", response_model=Auction)
def bid(id: str, amount_cents: int, db: Session = Depends(get_db)):
    a = db.query(AuctionModel).get(id)
    if not a or not a.active: raise HTTPException(404)
    if datetime.datetime.utcnow() >= a.ends_at: raise HTTPException(400, "Ended")
    if a.bin_price_cents and amount_cents >= a.bin_price_cents:
        a.current_bid_cents = a.bin_price_cents; a.high_bidder_id = "buyer"; a.active = False
    else:
        min_next = max(a.current_bid_cents + 100, 100)
        if amount_cents < min_next: raise HTTPException(400, f"Min {min_next}")
        a.current_bid_cents = amount_cents; a.high_bidder_id = "buyer"
    db.commit(); db.refresh(a)
    return Auction(**{k:getattr(a,k) for k in Auction.model_fields})

@app.get("/healthz")
def healthz(): return {"ok": True}
