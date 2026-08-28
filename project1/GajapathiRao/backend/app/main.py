import fastapi as fastapi

app = fastapi.FastAPI(
    title="Weather ETL API",
    version="1.0.0"
)

# app.include_router(weather_router)

@app.get("/")
def read_root():
     return {
        "message": "Weather ETL API is running"
    }
