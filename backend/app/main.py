from fastapi import FastAPI
from app.database import initialize_database
from fastapi.middleware.cors import CORSMiddleware
from app.router import api_router
from contextlib import asynccontextmanager
from app.database import client
from app.utils import verify_production_protection


@asynccontextmanager
async def lifespan(app: FastAPI):
    if not verify_production_protection():
        print("💥 CRITICAL: Cannot start server without production protection")
        raise RuntimeError(
            "Production protection required - server startup aborted"
        )
    await initialize_database()
    yield
    client.close()


app = FastAPI(
    title="my420.ca - Hepatitis C & HIV Testing Services",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(api_router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
