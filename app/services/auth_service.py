from fastapi import HTTPException, status
from app.clients.supabase_client import supabase, supabase_admin

def register_user(email: str, password: str):
    try:
        response = supabase.auth.sign_up({
            "email": email,
            "password": password
        })

        if not response.user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not register user"
            )

        if hasattr(response.user, "identities") and response.user.identities is not None and len(
                response.user.identities) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already registered"
            )

        return response.user
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

def authenticate_user(email: str, password: str):
    try:
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        if not response.session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        return response.session.access_token
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

def delete_supabase_user(user_id: str):
    try:
        res = supabase_admin.auth.admin.delete_user(user_id)
        if getattr(res, "status_code", None):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Supabase deletion failed: {res.error}"
            )
        print(f"--- DELETE FROM SUPABASE: {user_id} ---")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete user from Supabase Auth: {str(e)}"
        )