import json
from backend.main import app  # Импортируйте ваш FastAPI app

with open("openapi.json", "w") as f:
    json.dump(app.openapi(), f, indent=2)