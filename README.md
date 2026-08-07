# GradPilot

Evidence-driven graduate admissions decision-support platform.

## Current workflow

1. Upload multiple applicant documents (CV, transcript, GRE/TOEFL, research paper, SOP, other).
2. Merge them into a structured applicant profile and compute structured applicant-strength evidence.
3. Resolve university/program aliases to a canonical program.
4. Retrieve program evidence with official university sources prioritized.
5. Extract structured requirements, including alternative eligibility pathways and exceptions.
6. Run deterministic hard-requirement checks.
7. Keep program fit separate from program/admission competitiveness.
8. Produce an evidence-backed classification: Very High Reach / Reach / Target / Likely / Insufficient Evidence.
9. Historical-applicant utilities (normalization, import, statistics, similarity, reliability) are present as a secondary/experimental evidence layer; tiny or incomplete samples must not be treated as admission probabilities.

## Stack

- FastAPI + SQLAlchemy + Alembic
- PostgreSQL 16 + pgvector
- SentenceTransformers `all-MiniLM-L6-v2` (384 dimensions)
- Groq LLM
- Tavily retrieval
- Next.js 14 frontend
- Docker Compose database

## Local configuration

Copy `backend/.env.example` to `backend/.env` and fill in your own API keys. The checked-in configuration uses:

```env
DATABASE_URL=postgresql+psycopg2://gradpilot:gradpilot@localhost:5432/gradpilot
LLM_PROVIDER=groq
LLM_MODEL=llama-3.3-70b-versatile
EMBEDDING_PROVIDER=sentence_transformers
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
CORS_ORIGINS=http://localhost:3000
```

The Docker Compose database is exposed on host port **5432**, so the backend database URL must also use port **5432**.

## Run on Windows (existing local environment)

From the project root:

```cmd
docker compose up -d
docker compose ps
```

From `backend`:

```cmd
.venv\Scripts\activate
pip install -r requirements.txt
python -m alembic current
python -m alembic upgrade head
python -m uvicorn app.main:app --reload --port 8000
```

From `frontend` in a second terminal:

```cmd
npm install
npm run dev
```

Open `http://localhost:3000`.

## Migration order

The migration history is intentionally linear and matches the local workflow developed for this project:

`bd6f55d8bc74 -> e98e8ac7efec -> c31a7e42f9b1 -> 6e3b6d6f5875 -> 2f895c75588d -> 4e4dc6b13b10 -> 49e99f2f0ad1 -> a695242f983c -> 7c0a4f91b2d0`

If an existing database reports `6e3b6d6f5875`, `upgrade head` applies only the later migrations. The historical-table migration itself is duplicate-table safe.

## Important

Do not commit `.env`, `.env.local`, virtual environments, `node_modules`, `.next`, or API keys. Historical outcomes are self-reported observational evidence and are not admission probabilities.
