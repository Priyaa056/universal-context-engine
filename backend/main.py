import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.kb import router as kb_router
from api.retrieval import router as retrieval_router
from api.chat import router as chat_router
from config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.APP_TITLE,
    version=settings.APP_VERSION,
    description="Universal Context Engine with MCP Action Layer",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(kb_router)
app.include_router(retrieval_router)
app.include_router(chat_router)


def _configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )


_configure_logging()


@app.get("/")
def root():
    return {
        "status": "running",
        "project": "Universal Context Engine",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
    }
