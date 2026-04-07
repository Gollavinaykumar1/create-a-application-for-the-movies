# LLM Output

=== FILE: main.py ===
from fastapi import FastAPI
from database import init_db, get_db
from routers import items

app = FastAPI()

app.include_router(items.router)

@app.on_event("startup")
async def startup_event():
    await init_db()

@app.on_event("shutdown")
async def shutdown_event():
    await get_db().close()
=== END ===

=== FILE: models.py ===
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Movie(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True)
    title = Column(String)
    genre = Column(String)
    rating = Column(Integer)
=== END ===

=== FILE: database.py ===
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine, create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker
from models import Base
from typing import Optional

DATABASE_URL = os.getenv("DATABASE_URL")

engine: Optional[AsyncEngine] = None
SessionLocal: Optional[sessionmaker] = None

if DATABASE_URL:
    if DATABASE_URL.startswith("sqlite+aiosqlite://"):
        engine = create_async_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    elif DATABASE_URL.startswith("postgresql+asyncpg://"):
        engine = create_async_engine(DATABASE_URL)
    else:
        raise ValueError("Invalid DATABASE_URL")

    async def init_db():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def get_db():
        async with engine.begin() as conn:
            async_session = sessionmaker(
                engine, class_=AsyncSession, expire_on_commit=False, autocommit=False, autoflush=False
            )
            db = async_session()
            try:
                yield db
            finally:
                await db.close()
else:
    raise ValueError("DATABASE_URL not set")

async def init_db():
    if engine:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

async def get_db():
    if engine:
        async_session = sessionmaker(
            engine, class_=AsyncSession, expire_on_commit=False, autocommit=False, autoflush=False
        )
        async with async_session() as session:
            try:
                yield session
            finally:
                await session.close()
    else:
        raise ValueError("DATABASE_URL not set")
=== END ===

=== FILE: routers/items.py ===
from fastapi import APIRouter, Depends
from database import get_db
from models import Movie
from typing import List
from pydantic import BaseModel

router = APIRouter()

class MovieRequest(BaseModel):
    title: str
    genre: str
    rating: int

@router.get("/movies/")
async def read_movies(db: AsyncSession = Depends(get_db)):
    movies = await db.execute(Movie.select())
    return [{"id": movie.id, "title": movie.title, "genre": movie.genre, "rating": movie.rating} for movie in movies.scalars().all()]

@router.post("/movies/")
async def create_movie(movie: MovieRequest, db: AsyncSession = Depends(get_db)):
    db_movie = Movie(title=movie.title, genre=movie.genre, rating=movie.rating)
    db.add(db_movie)
    await db.commit()
    await db.refresh(db_movie)
    return {"id": db_movie.id, "title": db_movie.title, "genre": db_movie.genre, "rating": db_movie.rating}
=== END ===

=== FILE: requirements.txt ===
fastapi
uvicorn[standard]
sqlalchemy
aiosqlite
asyncpg
pydantic
python-dotenv
greenlet
=== END ===