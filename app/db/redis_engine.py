import redis.asyncio as redis
from app.config import settings


# -----------------------------
# Global Redis Client
# -----------------------------
redis_client : redis.Redis | None = None


# -----------------------------
# Initialize Redis
# -----------------------------
async def init_redis():
    global redis_client
    redis_client = redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=0,
        decode_responses=True
    )

    await redis_client.ping()


# -----------------------------
# Get Redis Client
# -----------------------------
def get_redis() -> redis.Redis:
    if redis_client is None:
        raise Exception("Redis is not initialized. Call init_redis() first")
    return redis_client


# -----------------------------
# Close Redis Connection
# -----------------------------
async def close_redis():
    global redis_client

    if redis_client:
        await redis_client.close()
        redis_client = None


# -----------------------------
# Add JTI to Blocklist
# -----------------------------
async def add_jti_to_blocklist(jti: str):
    await redis_client.set(jti, "revoked", ex=settings.JTI_EXPIRY)


# -----------------------------
# Check if Token is Revoked
# -----------------------------
async def token_in_blocklist(jti: str) -> bool:
    redis_client = get_redis()
    result = await redis_client.get(jti)
    return result is not None