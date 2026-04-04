from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.api.routes.analytics import router
from src.core.vector_store import init_vector_store

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_vector_store()      # warm up ChromaDB
    yield

app = FastAPI(title="Call Center Compliance API", lifespan=lifespan)
app.include_router(router)

@app.get("/health")
async def health():
    return {"status": "ok"}
