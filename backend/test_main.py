from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "message": "API de Películas funcionando 🎬"}

def test_create_and_get_movie():
    # 1. Crear una película de prueba
    movie_data = {"title": "Test Movie", "director": "Test Director", "year": 2024, "watched": False}
    response_post = client.post("/api/movies", json=movie_data)
    assert response_post.status_code == 200
    
    # 2. Verificar que se ha guardado en la lista
    response_get = client.get("/api/movies")
    assert response_get.status_code == 200
    movies = response_get.json()
    assert any(m["title"] == "Test Movie" for m in movies)