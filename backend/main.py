from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.application.routes import router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешить все домены (для разработки)
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

