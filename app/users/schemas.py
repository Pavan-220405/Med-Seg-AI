from pydantic import BaseModel
from typing import Optional
from uuid import UUID

class UserToken(BaseModel):
    user_id : UUID
    role : str 