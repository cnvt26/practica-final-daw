from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.orm import sessionmaker, Session, declarative_base
import os
import logging

# --- CONFIGURACIÓN DE LOGGING (Monitorización) ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("MovieAPI")

# --- CONFIGURACIÓN DE BASE DE DATOS ---
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./movies.db")
if DATABASE_URL.startswith("mysql://"):
    DATABASE_URL = DATABASE_URL.replace("mysql://", "mysql+pymysql://", 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class MovieDB(Base):
    __tablename__ = "movies"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), index=True)
    director = Column(String(100))
    year = Column(Integer)
    watched = Column(Boolean, default=False)

Base.metadata.create_all(bind=engine)

# --- FASTAPI ---
app = FastAPI(title="Mi Gestor de Películas API 🎬")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class MovieCreate(BaseModel):
    title: str
    director: str
    year: int
    watched: bool = False

class Movie(MovieCreate):
    id: int
    class Config:
        from_attributes = True

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- ENDPOINTS ---
@app.get("/")
def read_root():
    logger.info("Chequeo de salud del servidor solicitado.")
    return {"status": "ok", "message": "API de Películas funcionando 🎬"}

@app.get("/api/movies")
def get_movies(db: Session = Depends(get_db)):
    logger.info("Consultando la lista de películas.")
    return db.query(MovieDB).all()

@app.post("/api/movies")
def create_movie(movie: MovieCreate, db: Session = Depends(get_db)):
    db_movie = MovieDB(**movie.dict())
    db.add(db_movie)
    db.commit()
    db.refresh(db_movie)
    logger.info(f"Nueva película añadida: {movie.title} ({movie.year})")
    return db_movie

@app.put("/api/movies/{movie_id}")
def update_movie(movie_id: int, movie: MovieCreate, db: Session = Depends(get_db)):
    db_movie = db.query(MovieDB).filter(MovieDB.id == movie_id).first()
    if not db_movie:
        logger.warning(f"Intento de actualizar película inexistente (ID: {movie_id})")
        raise HTTPException(status_code=404, detail="Película no encontrada")
    for key, value in movie.dict().items():
        setattr(db_movie, key, value)
    db.commit()
    db.refresh(db_movie)
    logger.info(f"Película actualizada (ID: {movie_id})")
    return db_movie

@app.delete("/api/movies/{movie_id}")
def delete_movie(movie_id: int, db: Session = Depends(get_db)):
    db_movie = db.query(MovieDB).filter(MovieDB.id == movie_id).first()
    if not db_movie:
        logger.error(f"Fallo al eliminar: Película no encontrada (ID: {movie_id})")
        raise HTTPException(status_code=404, detail="Película no encontrada")
    db.delete(db_movie)
    db.commit()
    logger.info(f"Película eliminada (ID: {movie_id})")
    return {"message": "Película eliminada"}