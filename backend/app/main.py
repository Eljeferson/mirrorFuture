"""
FastAPI Production Entrypoint for MIRROR FUTURE.
Initializes the API server, CORS policy, causal routers, and actuator subsystems.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.routers.mirror_future_router import router as mirror_future_router
from app.routers.ingest_router import router as ingest_router

settings = get_settings()

app = FastAPI(
    title="Mirror Future - Causal AI Engine & Actuators",
    description="Causal Inference Engine, Monte Carlo Stochastic Simulation, and Temporal Oracle with Meta Llama 3.2/3.3",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration for frontend communication (Angular / Next.js / Vite)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(mirror_future_router, prefix="/api")
app.include_router(ingest_router, prefix="/api")


@app.get("/health", tags=["Health"])
async def health_check():
    """Production health check for the Mirror Future causal engine."""
    return {
        "status": "online",
        "service": "Mirror Future Causal Engine",
        "environment": settings.app_env,
        "models": {
            "vision": settings.llama_vision_model,
            "fast": settings.llama_fast_model,
            "reasoning": settings.llama_reasoning_model,
            "embeddings": settings.llama_embedding_model,
        },
        "actuators": {
            "calendar_ics": "enabled",
            "whatsapp_cloud_api": "enabled" if settings.whatsapp_api_token else "configured_without_token",
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
