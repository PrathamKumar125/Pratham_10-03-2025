from fastapi import FastAPI
from app.api.endpoints import router
from app.services.data_service import ingest_data
from app.db.database import check_data_exists
from app.core.config import logger
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        logger.info("Checking if data exists in the database...")
        if not check_data_exists():
            logger.info(
                "No data found in database, running initial data ingestion...")
            ingest_data()
    except Exception as e:
        logger.error(f"Startup error: {str(e)}")

    yield 

    logger.info("Shutting down application")

app = FastAPI(title="Store Monitoring System", lifespan=lifespan)

app.include_router(router)

@app.get("/")
async def root():
    return {
        "message": "Welcome to the Store Monitoring System API"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
