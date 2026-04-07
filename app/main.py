from fastapi import FastAPI
from contextlib import asynccontextmanager


from app.db.engine import init_db_pool, close_db_pool
from app.db.redis_engine import init_redis, close_redis
from app.users.routes import auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up...")
    # Startup code
    await init_db_pool()
    await init_redis()

    yield
    
    # Shutdown code
    print("Shutting down...")
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