from uuid import UUID
from typing import Optional
from sqlalchemy.orm import Session

from app.models.user import UserProfile

def get_profile_by_id(db: Session, user_id: UUID) -> Optional[UserProfile]:
    return db.query(UserProfile).filter(UserProfile.id == user_id).first()

def create_profile(db: Session, user_id: UUID) -> UserProfile:
    profile = UserProfile(id=user_id)
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile

def update_profile_fields(db: Session, profile: UserProfile, update_data: dict) -> UserProfile:
    for field, value in update_data.items():
        setattr(profile, field, value)
    db.commit()
    db.refresh(profile)
    return profile