# GradPilot — Milestone 1

AI Graduate Admissions Copilot. This milestone: upload CV -> structured profile ->
enter university/program -> retrieve official program info (RAG) -> fit analysis with evidence.

## Run

### 1. Database
```
docker compose up -d
```

### 2. Backend
```
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in ANTHROPIC_API_KEY, OPENAI_API_KEY, TAVILY_API_KEY
uvicorn app.main:app --reload
```

### 3. Frontend
```
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

Open http://localhost:3000

## Notes
- LLM provider: `LLM_PROVIDER=anthropic|openai` in backend/.env. Embeddings: `EMBEDDING_PROVIDER=openai`.
- Web search for official program pages uses Tavily (`TAVILY_API_KEY`). Without a key, use the
  "seed_url" or "manual_text" fields on the program step to supply program info directly.
- No fabrication: analysis only cites retrieved evidence chunks; missing info -> "Insufficient evidence".
- Not yet built (future milestones): SOP generator, application tracker, profile simulator,
  university comparison, auth, prediction ML model.
"# GradPilot" 
