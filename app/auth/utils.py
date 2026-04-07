import uuid
import bcrypt
import jwt
from fastapi import HTTPException, status
from datetime import datetime, timedelta, timezone


from app.config import settings
from app.users.schemas import UserToken

# -----------------------------
# Password Hashing
# -----------------------------
def hash_password(password : str) -> str:
    "Generate Hashed Password"

    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password=password.encode(),salt=salt)
    return hashed_password.decode()


# -----------------------------
# Password Verification
# -----------------------------
def verify_password(password : str, hashed_password : str) -> bool:
    "Verify actual and hashed passwords"

    return bcrypt.checkpw(password=password.encode(), hashed_password=hashed_password.encode())


# -----------------------------
# Create Access Token
# -----------------------------
def create_access_token(user_details : UserToken, expiry_time : timedelta = None):
    "Function to get access tokens"

    now = datetime.now(timezone.utc)
    expiry = now + (expiry_time if expiry_time else timedelta(minutes=settings.ACCESS_TOKEN_EXPIRY_MINUTES))
    payload = {
        "id" : str(user_details.id),
        "role" : user_details.role,
        "iat": int(now.timestamp()),
        "exp" : int(expiry.timestamp()),
        "type" : "access"
    }

    return jwt.encode(payload=payload,algorithm=settings.JWT_ALGORITHM,key=settings.JWT_SECRET_KEY) 


# -----------------------------
# Create Refresh Token
# -----------------------------
def create_refresh_token(user_details : UserToken, expiry_time : timedelta = None):
    "Function to get Refresh tokens" 

    now = datetime.now(timezone.utc)
    expiry = now + (expiry_time if expiry_time else timedelta(days=settings.REFRESH_TOKEN_EXPIRY_DAYS))
    payload = {
        "id" : str(user_details.id),
        "role" : user_details.role,
        "exp" : int(expiry.timestamp()),
        "iat": int(now.timestamp()),
        "type" : "refresh",
        "jti" : str(uuid.uuid4())
    }

    return jwt.encode(payload=payload,algorithm=settings.JWT_ALGORITHM,key=settings.JWT_SECRET_KEY) 



# -----------------------------
# Decode Access Token
# -----------------------------
def decode_access_token(token : str):
    try:
        payload = jwt.decode(jwt=token,key=settings.JWT_SECRET_KEY,algorithms=[settings.JWT_ALGORITHM])
        if payload.get("type") != "access":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid Token Type, Provide Access Token")
        if "id" not in payload:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid token payload")
        return payload
    
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Token Expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid Access Token")
    


# -----------------------------
# Decode Refresh Token
# -----------------------------
def decode_refresh_token(token : str):
    try:
        payload = jwt.decode(jwt=token,key=settings.JWT_SECRET_KEY,algorithms=[settings.JWT_ALGORITHM])
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid Token Type, Provide Refresh Token")
        if "id" not in payload or "jti" not in payload:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid Refresh Token")
        return payload
    
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Token Expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid Refresh Token")
