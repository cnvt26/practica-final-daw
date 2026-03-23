from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
import os
import logging

# --- CONFIGURACIÓN DE LOGGING ---
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("MovieAPI")

# --- CONFIGURACIÓN DE SEGURIDAD (JWT) ---
SECRET_KEY = os.getenv("SECRET_KEY", "super_secreta_cambiar_en_produccion")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# --- BASE DE DATOS ---
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./movies.db")
if DATABASE_URL.startswith("mysql://"):
    DATABASE_URL = DATABASE_URL.replace("mysql://", "mysql+pymysql://", 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Tablas de Base de Datos
class UserDB(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    hashed_password = Column(String(100))

class MovieDB(Base):
    __tablename__ = "movies"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), index=True)
    director = Column(String(100))
    year = Column(Integer)
    watched = Column(Boolean, default=False)

Base.metadata.create_all(bind=engine)

# --- FASTAPI APP ---
app = FastAPI(title="Gestor de Películas API 🎬 (Protegido)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- SCHEMAS (Pydantic) ---
class MovieCreate(BaseModel):
    title: str
    director: str
    year: int
    watched: bool = False

class UserCreate(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

# --- DEPENDENCIAS DE BASE DE DATOS Y AUTENTICACIÓN ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(UserDB).filter(UserDB.username == username).first()
    if user is None:
        raise credentials_exception
    return user

# --- ENDPOINTS DE AUTENTICACIÓN ---
@app.post("/register", response_model=dict)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(UserDB).filter(UserDB.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="El usuario ya existe")
    
    hashed_password = pwd_context.hash(user.password)
    new_user = UserDB(username=user.username, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    logger.info(f"Nuevo usuario registrado: {user.username}")
    return {"message": "Usuario creado con éxito. Ya puedes hacer login."}

@app.post("/token", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(UserDB).filter(UserDB.username == form_data.username).first()
    if not user or not pwd_context.verify(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = datetime.utcnow() + access_token_expires
    encoded_jwt = jwt.encode({"sub": user.username, "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)
    logger.info(f"Usuario logueado: {user.username}")
    return {"access_token": encoded_jwt, "token_type": "bearer"}

# --- ENDPOINTS DE PELÍCULAS (AHORA PROTEGIDOS 🔒) ---
@app.get("/")
def read_root():
    return {"status": "ok", "message": "API de Películas funcionando y protegida 🎬🔒"}

# Nota el `Depends(get_current_user)`: Esto exige que el usuario envíe un Token válido
@app.get("/api/movies")
def get_movies(db: Session = Depends(get_db), current_user: UserDB = Depends(get_current_user)):
    return db.query(MovieDB).all()

@app.post("/api/movies")
def create_movie(movie: MovieCreate, db: Session = Depends(get_db), current_user: UserDB = Depends(get_current_user)):
    db_movie = MovieDB(**movie.dict())
    db.add(db_movie)
    db.commit()
    db.refresh(db_movie)
    logger.info(f"Película añadida por {current_user.username}: {movie.title}")
    return db_movie

@app.put("/api/movies/{movie_id}")
def update_movie(movie_id: int, movie: MovieCreate, db: Session = Depends(get_db), current_user: UserDB = Depends(get_current_user)):
    db_movie = db.query(MovieDB).filter(MovieDB.id == movie_id).first()
    if not db_movie:
        raise HTTPException(status_code=404, detail="Película no encontrada")
    for key, value in movie.dict().items():
        setattr(db_movie, key, value)
    db.commit()
    db.refresh(db_movie)
    return db_movie

@app.delete("/api/movies/{movie_id}")
def delete_movie(movie_id: int, db: Session = Depends(get_db), current_user: UserDB = Depends(get_current_user)):
    db_movie = db.query(MovieDB).filter(MovieDB.id == movie_id).first()
    if not db_movie:
        raise HTTPException(status_code=404, detail="Película no encontrada")
    db.delete(db_movie)
    db.commit()
    logger.info(f"Película eliminada por {current_user.username}")
    return {"message": "Película eliminada"}