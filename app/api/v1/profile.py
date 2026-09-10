from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.domain import User, UserProfile
from app.schemas.domain import ProfileResponse, ProfileUpdate
from app.api.deps import get_current_user

router = APIRouter(prefix="/profile", tags=["Profile"])


@router.get("", response_model=ProfileResponse)
def get_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(UserProfile).filter(UserProfile.id == current_user.id).first()

    if not profile:
        profile = UserProfile(id=current_user.id)
        db.add(profile)
        db.commit()
        db.refresh(profile)

    return ProfileResponse(
        id=current_user.id,
        email=current_user.email,
        created_at=current_user.created_at,
        display_name=profile.display_name,
        daily_calorie_target=profile.daily_calorie_target,
        dietary_preferences=profile.dietary_preferences,
        allergies=profile.allergies,
        cooking_experience_level=profile.cooking_experience_level,
        preferred_cooking_time_minutes=profile.preferred_cooking_time_minutes,
    )


@router.put("", response_model=ProfileResponse)
def update_profile(
        profile_in: ProfileUpdate,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    profile = db.query(UserProfile).filter(UserProfile.id == current_user.id).first()

    if not profile:
        profile = UserProfile(id=current_user.id)
        db.add(profile)

    update_data = profile_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profile, field, value)

    db.commit()
    db.refresh(profile)

    return ProfileResponse(
        id=current_user.id,
        email=current_user.email,
        created_at=current_user.created_at,
        display_name=profile.display_name,
        daily_calorie_target=profile.daily_calorie_target,
        dietary_preferences=profile.dietary_preferences,
        allergies=profile.allergies,
        cooking_experience_level=profile.cooking_experience_level,
        preferred_cooking_time_minutes=profile.preferred_cooking_time_minutes,
    )

@router.delete("", response_model=ProfileResponse)
def delete_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(UserProfile).filter(UserProfile.id == current_user.id).first()

    response_data = ProfileResponse(
        id=current_user.id,
        email=current_user.email,
        created_at=current_user.created_at,
        display_name=profile.display_name if profile else None,
        daily_calorie_target=profile.daily_calorie_target if profile else None,
        dietary_preferences=profile.dietary_preferences if profile else None,
        allergies=profile.allergies if profile else None,
        cooking_experience_level=profile.cooking_experience_level if profile else None,
        preferred_cooking_time_minutes=profile.preferred_cooking_time_minutes if profile else None,
    )

    db.delete(current_user)
    db.commit()

    return response_data