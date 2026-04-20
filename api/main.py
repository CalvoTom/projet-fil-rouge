from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routers import running, climbing, cycling, swimming

app = FastAPI(
    title="Sport Predictor API",
    description="API de prédiction de performances sportives — Running, Escalade, Vélo, Natation",
    version="2.0.0",
)

# Port par défaut : 8008 (voir README pour lancer)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(running.router, prefix="/api/v1")
app.include_router(climbing.router, prefix="/api/v1")
app.include_router(cycling.router, prefix="/api/v1")
app.include_router(swimming.router, prefix="/api/v1")

@app.get("/")
def root():
    return {
        "name": "Sport Predictor API",
        "version": "2.0.0",
        "docs": "/docs",
        "endpoints": [
            "POST /api/v1/running/predict/simple",
            "POST /api/v1/running/predict/advanced",
            "POST /api/v1/climbing/predict",
            "POST /api/v1/cycling/predict/simple",
            "POST /api/v1/cycling/predict/advanced",
            "POST /api/v1/swimming/predict/simple",
            "POST /api/v1/swimming/predict/advanced",
        ]
    }

@app.get("/health")
def health():
    return {"status": "ok"}
