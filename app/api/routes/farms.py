from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from typing import List
import logging

from app.api.deps import get_current_user
from app.database import get_db
from app.models.farm import Farm
from app.models.user import User
from app.schemas.farm import FarmCreate, FarmResponse, CropHistory, Coordinates, SoilParameters
from app.api.routes.external import get_satellite_soil_data

router = APIRouter()

@router.get("", response_model=List[FarmResponse])
def get_farms(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(Farm).filter(Farm.user_id == current_user.id).all()


@router.post("", response_model=FarmResponse)
async def create_farm(
    farm_in: FarmCreate,
    auto_fetch_soil: bool = Query(True, description="Automatically fetch soil parameters from satellite data"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    logger = logging.getLogger(__name__)
    logger.info(f"Creating farm with auto_fetch_soil={auto_fetch_soil}")
    
    # Default empty soil params if none provided
    soil_params = {}
    
    # Extract coordinates for soil data fetching
    try:
        if farm_in.coordinates.lat == "string" or farm_in.coordinates.lng == "string":
            logger.warning("Invalid coordinates provided, using default soil data")
            soil_params = {
                "moisture": "Medium",
                "organic_carbon": "1.5%",
                "texture": "Sandy Loam",
                "ph": "6.8",
                "ec": "0.35 dS/m",
                "salinity": "Low", 
                "water_holding": "Medium",
                "organic_matter": "Medium",
                "npk": "N: Medium, P: Low, K: High"
            }
        else:
            lat = float(farm_in.coordinates.lat)
            lng = float(farm_in.coordinates.lng)
            
            # Auto-fetch soil data if either:
            # 1. auto_fetch_soil is True, or
            # 2. No soil_params were provided
            if auto_fetch_soil or farm_in.soil_params is None:
                logger.info(f"Auto-fetching soil data for coordinates: {lat}, {lng}")
                
                try:
                    # Fetch soil data
                    soil_data = await get_satellite_soil_data(
                        lat=lat,
                        lng=lng,
                        current_user=current_user
                    )
                    
                    # SoilData is now a SoilParameters object, convert to dict
                    if soil_data:
                        logger.info("Successfully fetched soil data")
                        soil_params = {
                            "moisture": soil_data.moisture,
                            "organic_carbon": soil_data.organic_carbon,
                            "texture": soil_data.texture,
                            "ph": soil_data.ph,
                            "ec": soil_data.ec or "",
                            "salinity": soil_data.salinity or "",
                            "water_holding": soil_data.water_holding or "",
                            "organic_matter": soil_data.organic_matter or "",
                            "npk": soil_data.npk or ""
                        }
                    else:
                        logger.warning("Soil data returned None, using default")
                        soil_params = {
                            "moisture": "Medium",
                            "organic_carbon": "1.5%",
                            "texture": "Sandy Loam",
                            "ph": "6.8",
                            "ec": "0.35 dS/m",
                            "salinity": "Low",
                            "water_holding": "Medium",
                            "organic_matter": "Medium",
                            "npk": "N: Medium, P: Low, K: High"
                        }
                except Exception as e:
                    logger.error(f"Error fetching soil data: {str(e)}")
                    # If auto-fetch fails, use default values
                    soil_params = {
                        "moisture": "Medium",
                        "organic_carbon": "1.5%",
                        "texture": "Sandy Loam",
                        "ph": "6.8",
                        "ec": "0.35 dS/m",
                        "salinity": "Low",
                        "water_holding": "Medium",
                        "organic_matter": "Medium",
                        "npk": "N: Medium, P: Low, K: High"
                    }
            # Use provided soil_params if auto-fetch is disabled
            elif farm_in.soil_params:
                logger.info("Using user-provided soil parameters")
                soil_params = farm_in.soil_params.dict()
    except Exception as e:
        logger.error(f"Error in create_farm: {str(e)}")
        soil_params = {
            "moisture": "Medium",
            "organic_carbon": "1.5%",
            "texture": "Sandy Loam",
            "ph": "6.8",
            "ec": "0.35 dS/m",
            "salinity": "Low",
            "water_holding": "Medium",
            "organic_matter": "Medium",
            "npk": "N: Medium, P: Low, K: High"
        }
    
    logger.info(f"Final soil params for farm: {soil_params}")
    
    # Create the farm with the appropriate soil parameters
    farm = Farm(
        user_id=current_user.id,
        name=farm_in.name,
        location=farm_in.location,
        size=farm_in.size,
        topography=farm_in.topography,
        coordinates=farm_in.coordinates.dict(),
        soil_params=soil_params,
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
async def update_farm(
    farm_id: str,
    farm_in: FarmCreate,
    auto_fetch_soil: bool = Query(True, description="Automatically fetch soil parameters from satellite data"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    farm = db.query(Farm).filter(Farm.id == farm_id, Farm.user_id == current_user.id).first()
    if not farm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Farm not found"
        )
    
    # Default to existing soil params
    soil_params = farm.soil_params
    
    # Extract coordinates for soil data fetching
    try:
        lat = float(farm_in.coordinates.lat)
        lng = float(farm_in.coordinates.lng)
        
        # Auto-fetch soil data if either:
        # 1. auto_fetch_soil is True, or
        # 2. No soil_params were provided
        if auto_fetch_soil or farm_in.soil_params is None:
            try:
                # Fetch soil data
                soil_data = await get_satellite_soil_data(lat=lat, lng=lng, current_user=current_user)
                
                # Convert Pydantic model to dict for database storage
                soil_params = {
                    "moisture": soil_data.moisture,
                    "organic_carbon": soil_data.organic_carbon,
                    "texture": soil_data.texture,
                    "ph": soil_data.ph,
                    "ec": soil_data.ec or "",
                    "salinity": soil_data.salinity or "",
                    "water_holding": soil_data.water_holding or "",
                    "organic_matter": soil_data.organic_matter or "",
                    "npk": soil_data.npk or ""
                }
            except Exception as e:
                # If fetching fails, keep existing soil params
                logging.error(f"Error fetching soil data during farm update: {str(e)}")
        # Use provided soil_params if auto-fetch is disabled and soil_params is provided
        elif farm_in.soil_params:
            soil_params = farm_in.soil_params.dict()
    except Exception as e:
        logging.error(f"Error in update_farm: {str(e)}")
        # Keep existing soil params if any error occurs
    
    # Update farm information
    farm.name = farm_in.name
    farm.location = farm_in.location
    farm.size = farm_in.size
    farm.topography = farm_in.topography
    farm.coordinates = farm_in.coordinates.dict()
    farm.soil_params = soil_params
    
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


@router.get("/soil-data", response_model=SoilParameters)
async def get_soil_data_for_farm(
    lat: float,
    lng: float,
    current_user: User = Depends(get_current_user)
):
    """
    Fetch soil data for a specific location.
    This endpoint is designed to be called from the frontend when a user adds or edits a farm,
    to automatically populate the soil parameters based on the farm's location.
    """
    # Reuse the existing satellite soil data endpoint
    soil_data = await get_satellite_soil_data(lat=lat, lng=lng, current_user=current_user)
    return soil_data


@router.put("/{farm_id}/update-soil", response_model=FarmResponse)
async def update_farm_soil_data(
    farm_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Automatically update a farm's soil data using satellite data based on the farm's coordinates.
    """
    logger = logging.getLogger(__name__)
    
    # Find the farm
    farm = db.query(Farm).filter(Farm.id == farm_id, Farm.user_id == current_user.id).first()
    if not farm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Farm not found"
        )
    
    try:
        # Extract coordinates
        lat = float(farm.coordinates.get("lat"))
        lng = float(farm.coordinates.get("lng"))
        
        logger.info(f"Updating soil data for farm {farm_id} at coordinates: {lat}, {lng}")
        
        # Fetch soil data
        soil_data = await get_satellite_soil_data(lat=lat, lng=lng, current_user=current_user)
        
        if not soil_data:
            logger.warning(f"No soil data returned for farm {farm_id}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch soil data"
            )
        
        # Update the farm's soil parameters - soil_data is now a SoilParameters object
        farm.soil_params = {
            "moisture": soil_data.moisture,
            "organic_carbon": soil_data.organic_carbon,
            "texture": soil_data.texture,
            "ph": soil_data.ph,
            "ec": soil_data.ec or "",
            "salinity": soil_data.salinity or "",
            "water_holding": soil_data.water_holding or "",
            "organic_matter": soil_data.organic_matter or "",
            "npk": soil_data.npk or ""
        }
        
        logger.info(f"Soil data for farm {farm_id} updated successfully")
        
        db.add(farm)
        db.commit()
        db.refresh(farm)
        
        return farm
    except Exception as e:
        logger.error(f"Failed to update soil data: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update soil data: {str(e)}"
        )


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