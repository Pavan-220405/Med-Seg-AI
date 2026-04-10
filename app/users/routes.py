from fastapi import APIRouter, Depends, HTTPException, status
from asyncpg import Connection


from app.users.schemas import UserSignup, UserLogin, UserResponse, UserToken, UserAdmin
from app.users.crud import crud_authenticate_user, crud_create_user, crud_make_user_admin
from app.auth.utils import create_access_token, create_refresh_token
from app.auth.dependencies import refresh_token_bearer, get_conn, RoleChecker, access_token_bearer
from app.db.redis_engine import add_jti_to_blocklist
from app.ML_models.crud import crud_get_all_models


auth_router = APIRouter()
admin_checker = RoleChecker(["admin"])




# ---------------------------
# User Signup Endpoint
# ---------------------------
@auth_router.post("/signup",status_code=status.HTTP_201_CREATED,response_model=UserResponse)
async def signup(user_details : UserSignup, conn : Connection = Depends(get_conn)):
    """Endpoint to register a new user. Accepts user details and creates a new user in the database"""
    
    try: 
        user = await crud_create_user(user_details, conn)
        if user:
            return UserResponse(**user)
    except HTTPException as e:
        raise e
    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while creating the user")
    


# ---------------------------
# User Login Endpoint
# ---------------------------
@auth_router.post("/login")
async def login(login_details : UserLogin, conn : Connection = Depends(get_conn)):
    """Endpoint to authenticate a user. Accepts email and password, verifies credentials, and returns user details along with access and refresh tokens."""
    
    try:
        user = await crud_authenticate_user(login_details, conn)
        if user:
            access_token = create_access_token(user_details=UserToken(id=user["id"], role=user["role"]))
            refresh_token = create_refresh_token(user_details=UserToken(id=user["id"], role=user["role"]))
            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user": UserResponse(**user)
            }
    except HTTPException as e:
        raise e
    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred during authentication")
    


# -------------------------------
# Get new refresh token Endpoint    
# -------------------------------
@auth_router.post('/refresh_token')
async def new_access_token(token_details = Depends(refresh_token_bearer)):

    new_access_token = create_access_token(user_details=UserToken(id=token_details["id"], role=token_details["role"]))
    return {"new_access_token" : new_access_token}



# -------------------------------
# Logout Endpoint
# -------------------------------   
@auth_router.post('/logout')
async def revoke_token(token_details = Depends(refresh_token_bearer)):
    jti = token_details["jti"]
    await add_jti_to_blocklist(jti=jti)

    return {"message" : "Logged Out Successfully"}




# -------------------------------
# Make Admin Endpoint
# -------------------------------
@auth_router.post('/make_admin',dependencies=[Depends(admin_checker)])
async def make_admin(new_user_email : UserAdmin, conn : Connection = Depends(get_conn)):
    result = await crud_make_user_admin(conn=conn , email=new_user_email.email)

    if result: 
        return {"message":f"Made user {new_user_email.email} as admin successfully"}
    
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User {new_user_email.email} doesn't exist")



# ----------------------------
# Get all active models
# ----------------------------
@auth_router.get("/",dependencies=[Depends(access_token_bearer)])
async def get_all_models(conn : Connection = Depends(get_conn)):
    return await crud_get_all_models(conn=conn)