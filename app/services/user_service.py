from sqlalchemy.orm import Session

from app.models.user import User, UserProfile
from app.schemas.user import ProfileResponse, ProfileUpdate
from app.repositories import user_repository


def get_or_create_profile(db: Session, user: User) -> UserProfile:
    profile = user_repository.get_profile_by_id(db, user.id)
    if not profile:
        profile = user_repository.create_profile(db, user.id)
    return profile


def build_profile_response(user: User, profile: UserProfile) -> ProfileResponse:
    return ProfileResponse(
        id=user.id,
        email=user.email,
        created_at=user.created_at,
        display_name=profile.display_name,
        daily_calorie_target=profile.daily_calorie_target,
        dietary_preferences=profile.dietary_preferences,
        allergies=profile.allergies,
        cooking_experience_level=profile.cooking_experience_level,
        preferred_cooking_time_minutes=profile.preferred_cooking_time_minutes,
    )


def update_profile(db: Session, user: User, profile_in: ProfileUpdate) -> ProfileResponse:
    profile = get_or_create_profile(db, user)
    update_data = profile_in.model_dump(exclude_unset=True)
    profile = user_repository.update_profile_fields(db, profile, update_data)
    return build_profile_response(user, profile)