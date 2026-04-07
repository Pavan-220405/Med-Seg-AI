import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

from fastapi import FastAPI
from contextlib import asynccontextmanager


from app.db.engine import init_db_pool, close_db_pool
from app.db.redis_engine import init_redis, close_redis
from app.users.routes import auth_router
from app.ML_models.Brain_Tumor_Segmentation.utils import init_model, close_model, get_model
from app.ML_models.Brain_Tumor_Segmentation.routes import segmentation_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up...")
    # Startup code
    await init_db_pool()
    await init_redis()
    init_model()

    model = get_model()
    yield   
    
    # Shutdown code
    print("Shutting down...")
    close_model()
    await close_db_pool()
    await close_redis()



version = "v1"
app = FastAPI(
    title="Med-Seg-AI API",
    description="API for user authentication and management in the Med-Seg-AI application",
    version=version,
    lifespan=lifespan
)


@app.get("/")
async def root():
    return {"message": "Welcome to the Med-Seg-AI API!"}

# Include Routers
app.include_router(auth_router,prefix=f"/api/{version}/users", tags=["Users"])
app.include_router(segmentation_router, prefix=f"/api/{version}/segmentation", tags=["Segmentation"])