from typing import List

from fastapi.security import HTTPBearer
from fastapi import Depends, HTTPException, Request, status
from asyncpg import Connection

from app.auth.utils import decode_access_token, decode_refresh_token
from app.db.redis_engine import token_in_blocklist
from app.users.crud import crud_get_user_by_id
from app.db.engine import get_pool


# ---------------------------
# Connection Dependency
# ---------------------------
async def get_conn():
    pool = get_pool()
    async with pool.acquire() as conn:
        yield conn



# -----------------------------
# Access Token Bearer
# -----------------------------
class AccessTokenBearer(HTTPBearer):
    def __init__(self, auto_error = True):
        super().__init__(auto_error=auto_error)
    
    async def __call__(self, request : Request) -> dict:            # __call__() makes an object behave like a function
        creds = await super().__call__(request)

        token = creds.credentials
        payload = decode_access_token(token)

        return payload
access_token_bearer = AccessTokenBearer()



# -----------------------------
# Refresh Token Bearer
# -----------------------------
class RefreshTokenBearer(HTTPBearer):
    def __init__(self, auto_error = True):
        super().__init__(auto_error=auto_error)
    
    async def __call__(self, request : Request) -> dict:
        creds = await super().__call__(request)

        token = creds.credentials
        payload = decode_refresh_token(token)

        if await token_in_blocklist(jti=payload["jti"]):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Refresh token revoked. Please login again")
        
        return payload
refresh_token_bearer = RefreshTokenBearer()




# ----------------------------
# Current User Dependency
# ----------------------------
async def get_curr_user(token_details : dict = Depends(access_token_bearer), conn : Connection = Depends(get_conn)):
    
    return await crud_get_user_by_id(conn=conn, id=token_details["id"])


# ----------------------------
# Role checker Dependency
# ----------------------------
class RoleChecker:
    def __init__(self, allowed_roles : List[str]) -> None:
        self.allowed_roles = allowed_roles
    
    async def __call__(self, token_details = Depends(access_token_bearer)):
        if token_details["role"] in self.allowed_roles:
            return True
        
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="You are not permitted to perform this action")