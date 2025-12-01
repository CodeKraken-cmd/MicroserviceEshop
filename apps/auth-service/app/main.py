import os, logging, uuid, datetime, json
from fastapi import FastAPI, Depends, HTTPException, Response, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from sqlalchemy import Column, String, DateTime, ForeignKey, create_engine, Boolean
from sqlalchemy.orm import declarative_base, Session, sessionmaker
from passlib.hash import bcrypt
from jose import jwt
from jose.utils import base64url_encode
from starlette.responses import JSONResponse

LOG_LEVEL = os.getenv("LOG_LEVEL","INFO")
logging.basicConfig(level=LOG_LEVEL)
logger = logging.getLogger("auth")

AUTH_AUD = os.getenv("AUTH_AUD", "shop-api")
AUTH_ISS = os.getenv("AUTH_ISS", "https://api.example.com")
CORS = os.getenv("CORS_ORIGINS","http://localhost:5173,http://localhost:5174").split(",")
DB_URL = os.getenv("AUTH_DB_URL","sqlite:///./auth.db")

PRIVATE_KEY_PATH = os.getenv("AUTH_PRIVATE_KEY_PATH","/app/keys/dev_rsa_private.pem")
KEY_ID = os.getenv("AUTH_KEY_ID","dev-key-1")

engine = create_engine(DB_URL, pool_pre_ping=True, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    roles = Column(String, default="user")
    email_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    token = Column(String, unique=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Auth Service (RS256)")
app.add_middleware(CORSMiddleware, allow_origins=CORS, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

def load_private_key():
    with open(PRIVATE_KEY_PATH, "rb") as f:
        return f.read()

def public_jwk_from_private(private_pem: bytes, kid: str):
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives.asymmetric import padding
    from cryptography.hazmat.primitives import hashes
    key = serialization.load_pem_private_key(private_pem, password=None, backend=default_backend())
    public_numbers = key.public_key().public_numbers()
    n = base64url_encode(public_numbers.n.to_bytes((public_numbers.n.bit_length() + 7) // 8, "big")).decode()
    e = base64url_encode(public_numbers.e.to_bytes((public_numbers.e.bit_length() + 7) // 8, "big")).decode()
    return {"kty":"RSA","kid":kid,"use":"sig","alg":"RS256","n":n,"e":e}

def issue_tokens(user: User):
    now = datetime.datetime.utcnow()
    access_payload = {
        "sub": user.id,
        "email": user.email,
        "roles": user.roles.split(","),
        "aud": AUTH_AUD,
        "iss": AUTH_ISS,
        "iat": now,
        "exp": now + datetime.timedelta(minutes=15)
    }
    access = jwt.encode(access_payload, load_private_key(), algorithm="RS256", headers={"kid": KEY_ID})
    refresh_token = str(uuid.uuid4())
    rt = RefreshToken(user_id=user.id, token=refresh_token, expires_at=now + datetime.timedelta(days=14))
    db = SessionLocal(); db.add(rt); db.commit(); db.close()
    return {"access_token": access, "token_type":"bearer", "refresh_token": refresh_token}

class RegisterIn(BaseModel):
    email: EmailStr
    password: str

class LoginIn(BaseModel):
    email: EmailStr
    password: str

class RefreshIn(BaseModel):
    refresh_token: str

@app.post("/register")
def register(body: RegisterIn):
    db = SessionLocal()
    try:
        u = db.query(User).filter_by(email=body.email).first()
        if u: raise HTTPException(400, "Email already registered")
        u = User(email=body.email, password_hash=bcrypt.hash(body.password), roles="admin,user")
        db.add(u); db.commit(); db.refresh(u)
        return {"id": u.id, "email": u.email}
    finally:
        db.close()

@app.post("/login")
def login(body: LoginIn):
    db = SessionLocal()
    try:
        u = db.query(User).filter_by(email=body.email).first()
        if not u or not bcrypt.verify(body.password, u.password_hash):
            raise HTTPException(401, "Invalid credentials")
        return issue_tokens(u)
    finally:
        db.close()

@app.post("/token/refresh")
def refresh(body: RefreshIn):
    db = SessionLocal()
    try:
        rt = db.query(RefreshToken).filter_by(token=body.refresh_token).first()
        if not rt or rt.expires_at < datetime.datetime.utcnow():
            raise HTTPException(401, "Invalid refresh")
        u = db.query(User).get(rt.user_id)
        if not u: raise HTTPException(401, "User missing")
        return issue_tokens(u)
    finally:
        db.close()

@app.get("/.well-known/jwks.json")
def jwks():
    jwk = public_jwk_from_private(load_private_key(), KEY_ID)
    return {"keys":[jwk]}

@app.get("/healthz")
def healthz(): return {"ok": True}

@app.get("/readyz")
def readyz(): return {"db": True}
