from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .db import engine, Base
from .routers import upload, program, analysis


app = FastAPI(
    title="GradPilot API",
    version="0.1.0"
)


# ---------------------------------------------------------
# CORS
# Allow the local Next.js frontend to communicate with
# the FastAPI backend.
# ---------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------
# ROUTERS
# ---------------------------------------------------------

app.include_router(upload.router)
app.include_router(program.router)
app.include_router(analysis.router)


# ---------------------------------------------------------
# DATABASE STARTUP
# ---------------------------------------------------------

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)


# ---------------------------------------------------------
# HEALTH CHECK
# ---------------------------------------------------------

@app.get("/api/health")
def health():
    return {
        "status": "ok"
    }