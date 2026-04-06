import asyncpg
from asyncpg import Pool
from typing import Optional

from app.config import settings


_pool : Optional[Pool] = None
# -------------------------
# Initialize DB Pool
# -------------------------
async def init_db_pool():
    "Initialize Database Connection Pool"

    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(
            dsn=settings.DATABASE_URL,
            min_size=1,
            max_size=20
        )



# -------------------------
# Get Pool
# -------------------------
async def get_pool():
    "Get the initialized database connection pool"

    if _pool is None:
        raise RuntimeError("DB Pool is not initialized, call init_db_pool first")
    return _pool



# -------------------------
# Close DB Pool
# -------------------------
async def close_db_pool():
    "Close Database Connection Pool"

    global _pool
    if _pool:
        await _pool.close()
        _pool = None 