from fastapi.testclient import TestClient

# Change this import if your FastAPI file has a different name.
from app.main import app

client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "message": "Welcome to DOCUMIND AI ",
        "Success": 200,
    }
def test_openapi_schema_is_available():
    response = client.get("/openapi.json")

    assert response.status_code == 200

    schema = response.json()
    assert "paths" in schema
    assert "/" in schema["paths"]