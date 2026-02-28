from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.orm import sessionmaker, Session, declarative_base
import os

# 1. Configuración de la Base de Datos
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./movies.db")
# Adaptación automática para Railway (cambia mysql:// por mysql+pymysql://)
if DATABASE_URL.startswith("mysql://"):
    DATABASE_URL = DATABASE_URL.replace("mysql://", "mysql+pymysql://", 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 2. Modelo de la Base de Datos (SQL)
class MovieDB(Base):
    __tablename__ = "movies"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), index=True)
    director = Column(String(100))
    year = Column(Integer)
    watched = Column(Boolean, default=False)

# Crear las tablas automáticamente
Base.metadata.create_all(bind=engine)

# 3. Configuración de FastAPI
app = FastAPI(title="Mi Gestor de Películas API 🎬")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Permite que el frontend de Vercel se conecte
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 4. Esquemas Pydantic (Validación de datos)
class MovieCreate(BaseModel):
    title: str
    director: str
    year: int
    watched: bool = False

class Movie(MovieCreate):
    id: int
    class Config:
        from_attributes = True

# Dependencia para usar la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 5. Endpoints (Rutas de la API)
@app.get("/")
def read_root():
    return {"status": "ok", "message": "API de Películas funcionando 🎬"}

@app.get("/api/movies")
def get_movies(db: Session = Depends(get_db)):
    return db.query(MovieDB).all()

@app.post("/api/movies")
def create_movie(movie: MovieCreate, db: Session = Depends(get_db)):
    db_movie = MovieDB(**movie.dict())
    db.add(db_movie)
    db.commit()
    db.refresh(db_movie)
    return db_movie

@app.put("/api/movies/{movie_id}")
def update_movie(movie_id: int, movie: MovieCreate, db: Session = Depends(get_db)):
    db_movie = db.query(MovieDB).filter(MovieDB.id == movie_id).first()
    if not db_movie:
        raise HTTPException(status_code=404, detail="Película no encontrada")
    for key, value in movie.dict().items():
        setattr(db_movie, key, value)
    db.commit()
    db.refresh(db_movie)
    return db_movie

@app.delete("/api/movies/{movie_id}")
def delete_movie(movie_id: int, db: Session = Depends(get_db)):
    db_movie = db.query(MovieDB).filter(MovieDB.id == movie_id).first()
    if not db_movie:
        raise HTTPException(status_code=404, detail="Película no encontrada")
    db.delete(db_movie)
    db.commit()
    return {"message": "Película eliminada"}