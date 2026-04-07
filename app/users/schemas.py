from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Annotated, Literal
from uuid import UUID

class UserToken(BaseModel):
    id : UUID
    role : str 


class UserSignup(BaseModel):
    user_name : str = Field(..., description="Unique username for the user must be at least 4 characters long", min_length=4)
    first_name : str = Field(..., description="First name of the user")
    last_name : str = Field(..., description="Last name of the user")
    email : EmailStr
    password : str = Field(..., description="Password must be at least 8 characters long", min_length=8)
    role : Literal["radiologist", "user"] = Field(default='user', description="Role of the user, either 'radiologist' or 'user'. 'admin' can't be assigned during signup, it can only be assigned by an existing admin")

class UserLogin(BaseModel):
    email : EmailStr
    password : str = Field(..., description="Password must be at least 8 characters long", min_length=8)



class UserResponse(BaseModel):
    id : UUID
    user_name : str
    first_name : str
    last_name : str
    email : EmailStr
    role : str


class UserAdmin(BaseModel):
    email : EmailStr