from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg2://gradpilot:gradpilot@localhost:5432/gradpilot"

    llm_provider: str = "groq"
    llm_model: str = "llama-3.3-70b-versatile"
    anthropic_api_key: str = ""
    groq_api_key: str = ""

    embedding_provider: str = "sentence_transformers"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    openai_api_key: str = ""

    tavily_api_key: str = ""

    # Community-reported outcome data (GradCafe, Reddit r/gradadmissions, etc.) as a distinct,
    # capped-trust evidence tier — self-reported and unverifiable, so it's kept separate from
    # official structured_requirements and never allowed to override an official requirement
    # failure. Review the target sites' terms of service for your deployment before enabling in
    # production; this defaults on because it was explicitly requested, but is a config toggle
    # specifically so it can be turned off per-deployment if that review turns up a concern.
    enable_community_outcome_evidence: bool = True

    cors_origins: str = "http://localhost:3000"

    class Config:
        env_file = ".env"


settings = Settings()
