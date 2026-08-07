# Reconciled local workflow

This package was cleaned to remove the discrepancies found in the uploaded working tree.

- Docker and backend DB port are standardized on `5432`.
- Frontend is `http://localhost:3000`; backend CORS default/example matches it.
- Groq configuration is standardized on `llama-3.3-70b-versatile`.
- MiniLM configuration is standardized on `sentence-transformers/all-MiniLM-L6-v2`, vector dimension 384.
- Alembic was linearized to the actual local development sequence, with the historical migration after `c31a7e42f9b1`.
- Duplicate `official_domain` / `structured_requirements` additions were removed from the later canonical-program migration because `c31a7e42f9b1` already creates them.
- `user_provided_only` migration now safely backfills existing program rows before removing its server default.
- Historical services, Applicant Strength, conditional eligibility extraction, program resolution, official-first retrieval and classification guardrails are retained.
- Generated folders, virtual environments, secrets, and the accidentally nested duplicate `gradpilot/gradpilot` tree are excluded from the clean ZIP.
