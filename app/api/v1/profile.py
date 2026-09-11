from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.schemas.user import ProfileResponse, ProfileUpdate
from app.api.deps import get_current_user
from app.services import user_service
from app.services.auth_service import delete_supabase_user

router = APIRouter(prefix="/profile", tags=["Profile"])

@router.get("", response_model=ProfileResponse)
def get_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = user_service.get_or_create_profile(db, current_user)
    return user_service.build_profile_response(current_user, profile)

@router.put("", response_model=ProfileResponse)
def update_profile(
        profile_in: ProfileUpdate,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    return user_service.update_profile(db, current_user, profile_in)

@router.delete("", response_model=ProfileResponse)
def delete_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = user_service.get_or_create_profile(db, current_user)
    response_data = user_service.build_profile_response(current_user, profile)

    delete_supabase_user(str(current_user.id))

    try:
        db.delete(current_user)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Supabase user deleted, but local cleanup failed: {str(e)}"
        )
    return response_data