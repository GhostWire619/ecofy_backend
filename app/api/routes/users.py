from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserBase, UserResponse

router = APIRouter()

@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user


@router.put("/me", response_model=UserResponse)
def update_user(
    user_in: UserBase,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Update user information
    current_user.full_name = user_in.full_name
    current_user.phone_number = user_in.phone_number
    current_user.location = user_in.location
    current_user.preferred_language = user_in.preferred_language
    
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    
    return current_user


@router.patch("/language", response_model=dict)
def update_language(
    language_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    preferred_language = language_data.get("preferred_language")
    if not preferred_language:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Preferred language is required"
        )
    
    current_user.preferred_language = preferred_language
    db.add(current_user)
    db.commit()
    
    return {
        "success": True,
        "preferred_language": preferred_language
    } 