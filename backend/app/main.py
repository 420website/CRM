from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.logger import logger
from app.authentication.router import router as auth_router
from app.references.router import router as reference_router
from app.registration.router import router as patient_router
from app.analytics.router import router as analytics_router
from app.webpage.router import router as contact_router
from app.share_links.router import router as share_link_router
from app.zoom.router import router as video_router
from app.objects.router import router as object_router
from app.config import settings
from app.database import database, minio_client
from app.database import redis_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.connect()
    await minio_client.connect()
    await redis_client.connect()
    logger.info("Application startup complete")
    yield

    logger.info("Application shutdown initiated")
    await redis_client.disconnect()
    await minio_client.disconnect()
    await database.disconnect()
    logger.info("Application shutdown complete")


app = FastAPI(
    title="my420.ca - Hepatitis C & HIV Testing Services",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    max_age=3600,
)


@app.get("/health")
def health_check():
    return {"status": "ok"}


# Include routers
app.include_router(auth_router)
app.include_router(contact_router)
app.include_router(analytics_router)
app.include_router(reference_router)
app.include_router(patient_router)
app.include_router(share_link_router)
app.include_router(object_router)
app.include_router(video_router)

if settings.debug:
    from app.testing.router import router as testing_router

    app.include_router(testing_router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        timeout_keep_alive=300,  # 5 minutes
        limit_concurrency=1000,
        limit_max_requests=10000,
    )
