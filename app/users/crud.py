from asyncpg import Connection, UniqueViolationError
from fastapi import HTTPException, status
from uuid import UUID

from app.users.schemas import UserSignup, UserLogin
from app.auth.utils import hash_password, verify_password



async def crud_create_user(user_details : UserSignup, conn : Connection):
    """Creates a new user in the database with the provided details."""

    hashed_password = hash_password(user_details.password)
    query = """
            INSERT INTO users(user_name, first_name, last_name, email, hashed_password, role)
            VALUES ($1,$2,$3,$4,$5,$6)
            RETURNING *
        """
    
    try: 
        row = await conn.fetchrow(
            query,
            user_details.user_name,
            user_details.first_name,
            user_details.last_name,
            user_details.email,
            hashed_password,
            user_details.role
        )
        return dict(row) if row else None
    
    except UniqueViolationError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"user {user_details.email} already exists")
    



async def crud_authenticate_user(login_details : UserLogin, conn : Connection):
    """Authenticates a user by verifying the provided email and password against the database records."""

    query = """
            SELECT * FROM users WHERE email = $1
        """
    row = await conn.fetchrow(query, login_details.email)
    
    if row and verify_password(login_details.password, row['hashed_password']):
        return dict(row)
    
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")




async def crud_get_user_by_id(id : UUID, conn : Connection):
    """Retrieves a user's details from the database using their unique identifier."""

    query = """
            SELECT * FROM users WHERE id = $1
        """
    row = await conn.fetchrow(query, id)
    
    if row:
        return dict(row)
    
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User {id} not found")



async def crud_get_user_by_email(email : str, conn : Connection):
    """Retrieves a user's details from the database using their email address."""

    query = """
            SELECT * FROM users WHERE email = $1
        """
    row = await conn.fetchrow(query, email)
    
    if row:
        return dict(row)
    
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with email {email} not found")




async def crud_delete_user_by_id(id : UUID, conn : Connection):
    """Deletes a user from the database using their unique identifier."""

    query = """
            DELETE FROM users WHERE id = $1
            RETURNING *
        """
    result = await conn.fetchrow(query, id)
    
    if result:
        return {"message": f"User {id} deleted successfully"}
    
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User {id} not found")




async def crud_delete_user_by_email(email : str, conn : Connection):
    """Deletes a user from the database using their email address."""

    query = """
            DELETE FROM users WHERE email = $1
            RETURNING *
        """
    result = await conn.fetchrow(query, email)
    
    if result:
        return {"message": f"User with email {email} deleted successfully"}
    
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with email {email} not found")




async def crud_make_user_admin(email : str, conn : Connection):
    """Updates a user's role to 'admin' in the database using their email. Only an existing admin can perform this action."""

    query = """
            UPDATE users SET role = 'admin' WHERE email = $1
            RETURNING *
        """
    result = await conn.fetchrow(query, email)
    return dict(result) if result else None
