# AUTHservice Microshop (Production-Ready Scaffold)

This is a runnable microservices scaffold that combines ideas from clients:
- Catalog + Listings (offers & buy box)
- Cart, Orders, Payments (with escrow), Auctions, Reviews, RFQ
- Auth with HS256 (shared secret) by default; JWKS/RS256 optional
- API Gateway (Nginx), Docker Compose for dev, separate frontends (web + admin)
- Shared Python libs for JWT verification, DB helpers, telemetry stubs

## Dev quickstart

```bash
cd deploy
cp .env.example .env
docker compose -f docker-compose.dev.yml up --build
```

Admin: http://localhost:5174  
Web:   http://localhost:5173  
Gateway proxies APIs under http://localhost/api/*

### Auth defaults
- Use shared secret (HS256) by default via `AUTH_SHARED_SECRET` in `.env`.
- You can switch to RS256 by removing `AUTH_SHARED_SECRET` and providing JWKS at `/.well-known/jwks.json` in auth service (see comments in `apps/auth-service/app/routes.py`).

### Services
- auth, catalog, listings, cart, order, payment, reviews, auctions, rfq, search
- infra: Postgres (auth/catalog/order), Redis (cart/auctions), NATS (events stub), OpenSearch (placeholder API)

### Production notes
- Replace dev secrets with a secrets manager (AWS Secrets Manager)
- Add Alembic migrations (models create tables on startup for dev)
- Add OpenTelemetry collector + Prometheus, Grafana, Loki
- Move to Helm charts (deploy/k8s/helm) and Terraform (deploy/terraform)

IMPORTANT: Generate a real RSA key for auth in production and set AUTH_PRIVATE_KEY_PATH.
