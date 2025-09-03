from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.authentication.router import router as auth_router
from app.general.router import router as general_router
from app.registration.router import router as patient_router
from app.analytics.router import router as analytics_router
from app.webpage.router import router as contact_router
from app.config import settings
from app.database import database


@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.connect()
    yield
    await database.disconnect()


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
)

# Include routers
app.include_router(auth_router)
app.include_router(contact_router)
app.include_router(analytics_router)
app.include_router(general_router)
app.include_router(patient_router)


@app.get("/health")
def health_check():
    return {"status": "ok"}


if settings.debug:
    from app.testing.router import router as testing_router

    app.include_router(testing_router)
