from uuid import UUID
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, ConfigDict

# USER SCHEMAS

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str
    display_name: str

class RegistrationResponse(BaseModel):
    id: UUID
    email: EmailStr
    display_name: str

    model_config = ConfigDict(from_attributes=True)

class UserResponse(UserBase):
    id: UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class UserLogin(UserBase):
    password: str

# PROFILE SCHEMAS

class ProfileBase(BaseModel):
    display_name: Optional[str] = None
    daily_calorie_target: Optional[int] = None
    dietary_preferences: Optional[List[str]] = None
    allergies: Optional[List[str]] = None
    cooking_experience_level: Optional[str] = None
    preferred_cooking_time_minutes: Optional[int] = None

class ProfileResponse(ProfileBase):
    id: UUID
    email: EmailStr
    created_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)

class ProfileUpdate(ProfileBase):
    pass

