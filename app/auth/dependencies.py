from fastapi.security import HTTPBearer
from fastapi import Request, Depends, HTTPException, status
from asyncpg import Connection


from app.auth.utils import decode_access_token, decode_refresh_token
from app.db.engine import get_pool


# ---------------------------------
# Database connection dependency
# ---------------------------------
async def get_conn():
    pool = get_pool()
    async with pool.acquire() as conn:
        yield conn



# ----------------------------------
# Access Token Bearer dependency
# ----------------------------------
class AccessTokenBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request : Request):
        creds = await super().__call__(request)

        token = creds.credentials
        payload = decode_access_token(token)
        return payload
    
access_token_bearer = AccessTokenBearer()
    


# ----------------------------------
# Refresh Token Bearer dependency
# ----------------------------------
class RefreshTokenBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request : Request):
        creds = await super().__call__(request)

        token = creds.credentials
        payload = decode_refresh_token(token)
        return payload
    
refresh_token_bearer = RefreshTokenBearer()



# ----------------------------------
# Get Current User Dependency
# ----------------------------------
async def get_current_user(payload : dict = Depends(access_token_bearer), conn : Connection = Depends(get_conn)):
    id = payload["id"]
    pass 




# ----------------------------------
# Role Checker Dependency
# ----------------------------------
class RoleChecker:
    def __init__(self, allowed_roles : list):
        self.allowed_roles = allowed_roles

    async def __call__(self, payload = Depends(access_token_bearer)):
        if payload["role"] not in self.allowed_roles:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="You're not authorized to perform this action")
        
        return True
        