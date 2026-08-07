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



## Important

Do not commit `.env`, `.env.local`, virtual environments, `node_modules`, `.next`, or API keys. Historical outcomes are self-reported observational evidence and are not admission probabilities.
