from fastapi import APIRouter, Depends, Response, status, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.domain import User, UserProfile
from app.schemas.domain import UserCreate, RegistrationResponse, UserResponse, UserLogin
from app.services.auth_service import register_user, authenticate_user
from app.api.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post(
    "/register",
    response_model=RegistrationResponse,
    status_code=status.HTTP_201_CREATED
)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    try:
        supabase_user = register_user(user_in.email, user_in.password)
    except HTTPException as e:
        raise e

    existing_user = db.query(User).filter(User.id == supabase_user.id).first()
    if existing_user:
        profile = db.query(UserProfile).filter(UserProfile.id == existing_user.id).first()
        return RegistrationResponse(
            id=existing_user.id,
            email=existing_user.email,
            display_name=profile.display_name if profile else user_in.display_name
        )

    new_user = User(
        id=supabase_user.id,
        email=user_in.email
    )

    new_profile = UserProfile(
        id=supabase_user.id,
        display_name=user_in.display_name
    )

    db.add(new_user)
    db.add(new_profile)
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create local user record: {str(e)}"
        )

    return RegistrationResponse(
        id=new_user.id,
        email=new_user.email,
        display_name=new_profile.display_name
    )

@router.post("/login")
def login(user_in: UserLogin, response: Response, db: Session = Depends(get_db)):
    access_token = authenticate_user(user_in.email, user_in.password)

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=60 * 60 * 24
    )

    user = db.query(User).filter(User.email == user_in.email).first()
    if not user:
        print(f"--- WARNING: local user missing for {user_in.email}, recreating from Supabase ---")
        from app.clients.supabase_client import supabase
        user_response = supabase.auth.get_user(access_token)
        sup_user = user_response.user

        user = User(id=sup_user.id, email=sup_user.email)
        profile = UserProfile(id=sup_user.id, display_name=sup_user.email.split("@")[0])
        db.add(user)
        db.add(profile)
        try:
            db.commit()
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to create local user record: {str(e)}"
            )

    return {"id": user.id, "email": user.email}

@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(response: Response):
    response.delete_cookie(key="access_token")

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user