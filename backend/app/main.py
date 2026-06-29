from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.api.routes import cluster, collection, playlists, tracks, users
from app.core.config import settings
from app.core.database import AsyncSessionLocal, engine


# TODO: change the name of this directory / associated repo from spotify-playlist-recommender to playlist-recommender
@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await engine.dispose()


app = FastAPI(
    title="Playlist Recommender",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(users.router)
app.include_router(tracks.router)
app.include_router(collection.router)
app.include_router(playlists.router)
app.include_router(cluster.router)

@app.get("/health")
async def health():
    async with AsyncSessionLocal() as session:
        await session.execute(text("SELECT 1"))
    return {"status": "ok", "environment": settings.environment}
