from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Annotated, Literal
from uuid import UUID

class UserToken(BaseModel):
    id : UUID
    role : str 


class UserSignup(BaseModel):
    user_name : Annotated[str,Field("Username must be at least 6 characters long", min_length=6)]
    first_name : Annotated[str,Field("First name of the user")]
    last_name : Annotated[str,Field("Last name of the user")]
    email : EmailStr
    password : Annotated[str,Field("Password must be at least 8 characters long", min_length=8)]
    role : Annotated[Literal['user','radiologist'],Field("Role must be either 'user' or 'radiologist', admin role is not allowed to be created through this endpoint")] = 'user'


class UserLogin(BaseModel):
    email : EmailStr
    password : Annotated[str,Field("Password must be at least 8 characters long", min_length=8)]



class UserResponse(BaseModel):
    id : UUID
    user_name : str
    first_name : str
    last_name : str
    email : EmailStr
    role : str


class UserAdmin(BaseModel):
    email : Annotated[EmailStr,Field(description="Email of the new user to make him as admin")] 
