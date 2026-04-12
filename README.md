# Lumina — High-Reliability Billing Service

A production-grade subscription billing backend built to handle 
complex payment lifecycles with financial-grade reliability.

## What it does
Lumina manages subscription billing end-to-end — creating subscriptions, 
generating invoices, processing payments, and handling edge cases like 
duplicate charges and invalid state transitions.

## Tech Stack
- **Python + FastAPI** — backend web framework
- **PostgreSQL** — database for financial data
- **psycopg2** — database driver connecting Python to PostgreSQL

## Key Engineering Concepts
- **Atomic transactions** — subscription and invoice created together or rolled back entirely
- **State machine** — enforces ACTIVE → PAST_DUE → CANCELED transitions
- **Idempotency** — unique keys per payment request prevent duplicate charges
- **Foreign key constraints** — database-level data integrity

## Phases
- **Phase 1** — Core engine: schema design, REST API, state machine
- **Phase 2** — Reliability: idempotency middleware, atomic transactions
- **Phase 3** — Scale: Redis background workers, exponential backoff, structured logging

## Running locally
```bash
git clone https://github.com/AneeshGaju/lumina
cd lumina
python -m venv venv
source venv/bin/activate
pip install fastapi uvicorn psycopg2-binary
uvicorn main:app --reload
```
