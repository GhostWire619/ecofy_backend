from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List

from app.api.deps import get_current_user
from app.database import get_db
from app.models.farm import Farm
from app.models.user import User
from app.schemas.farm import FarmCreate, FarmResponse, CropHistory

router = APIRouter()

@router.get("", response_model=List[FarmResponse])
def get_farms(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(Farm).filter(Farm.user_id == current_user.id).all()


@router.post("", response_model=FarmResponse)
def create_farm(
    farm_in: FarmCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    farm = Farm(
        user_id=current_user.id,
        name=farm_in.name,
        location=farm_in.location,
        size=farm_in.size,
        topography=farm_in.topography,
        coordinates=farm_in.coordinates.dict(),
        soil_params=farm_in.soil_params.dict(),
        crop_history=[]
    )
    
    db.add(farm)
    db.commit()
    db.refresh(farm)
    
    return farm


@router.get("/{farm_id}", response_model=FarmResponse)
def get_farm(
    farm_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    farm = db.query(Farm).filter(Farm.id == farm_id, Farm.user_id == current_user.id).first()
    if not farm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Farm not found"
        )
    
    return farm


@router.put("/{farm_id}", response_model=FarmResponse)
def update_farm(
    farm_id: str,
    farm_in: FarmCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    farm = db.query(Farm).filter(Farm.id == farm_id, Farm.user_id == current_user.id).first()
    if not farm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Farm not found"
        )
    
    # Update farm information
    farm.name = farm_in.name
    farm.location = farm_in.location
    farm.size = farm_in.size
    farm.topography = farm_in.topography
    farm.coordinates = farm_in.coordinates.dict()
    farm.soil_params = farm_in.soil_params.dict()
    
    db.add(farm)
    db.commit()
    db.refresh(farm)
    
    return farm


@router.delete("/{farm_id}", response_model=dict)
def delete_farm(
    farm_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    farm = db.query(Farm).filter(Farm.id == farm_id, Farm.user_id == current_user.id).first()
    if not farm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Farm not found"
        )
    
    db.delete(farm)
    db.commit()
    
    return {"success": True}


@router.post("/{farm_id}/crop-history", response_model=FarmResponse)
def add_crop_history(
    farm_id: str,
    crop_history: CropHistory,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    farm = db.query(Farm).filter(Farm.id == farm_id, Farm.user_id == current_user.id).first()
    if not farm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Farm not found"
        )
    
    # Add crop history
    if not farm.crop_history:
        farm.crop_history = []
    
    farm.crop_history.append(crop_history.dict())
    
    db.add(farm)
    db.commit()
    db.refresh(farm)
    
    return farm


@router.post("/{farm_id}/image", response_model=dict)
async def upload_farm_image(
    farm_id: str,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    farm = db.query(Farm).filter(Farm.id == farm_id, Farm.user_id == current_user.id).first()
    if not farm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Farm not found"
        )
    
    # In a real app, you would upload the file to cloud storage
    # For demo purposes, we'll just pretend the image was uploaded
    image_url = f"/uploads/farms/{farm_id}/{file.filename}"
    
    # Update farm with image URL
    farm.image = image_url
    db.add(farm)
    db.commit()
    
    return {"image_url": image_url} 