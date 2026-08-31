from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import etl_router, locations_router, news_router, weather_router


def create_app() -> FastAPI:
    app = FastAPI(title="Weather ETL API", version="1.0.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(weather_router)
    app.include_router(locations_router)
    app.include_router(news_router)
    app.include_router(etl_router)

    @app.get("/")
    def read_root():
        return {"message": "Weather ETL API is running"}

    return app
