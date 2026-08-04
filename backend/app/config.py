from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg2://gradpilot:gradpilot@localhost:5432/gradpilot"

    # LLM
    llm_provider: str = "groq"
    llm_model: str = "llama-3.3-70b-versatile"
    groq_api_key: str = ""

    # Local embeddings
    embedding_provider: str = "local"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"

    # University web search
    tavily_api_key: str = ""

    cors_origins: str = "http://localhost:3000"

    class Config:
        env_file = ".env"


settings = Settings()