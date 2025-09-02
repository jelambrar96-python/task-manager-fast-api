from fastapi.middleware.cors import CORSMiddleware

from app.core.config import CORS_HEADERS, CORS_METHODS, CORS_ORIGINS


origins = [ "http://localhost", "http://localhost:8080", "http://frontend", "http://frontend:8080"] \
        if CORS_ORIGINS is None else CORS_ORIGINS.split(",")

methods = ["GET", "POST", "PUT", "DELETE"] if CORS_METHODS else CORS_METHODS.split(",")
headers = ["Authorization", "Content-Type"] if CORS_HEADERS else CORS_HEADERS.split(",")


def add_cors_middleware(app):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=methods,
        allow_headers=headers,
    )
