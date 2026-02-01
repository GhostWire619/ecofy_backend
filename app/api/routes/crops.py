from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, UploadFile, File, Request, Form
from pathlib import Path as LocalPath
import json
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from math import ceil

from app.api.deps import get_current_user
from app.database import get_db
from app.models.crop import Crop
from app.models.market import MarketPrice
from app.models.farm import Farm
from app.models.user import User
from app.schemas.crop import CropResponse, CropCreate
from app.schemas.market import MarketData

router = APIRouter()

@router.get("", response_model=Dict[str, Any])
def get_crops(
    request: Request,
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    name: Optional[str] = Query(None, description="Filter by crop name"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get paginated list of crops with optional filtering by name.
    """
    query = db.query(Crop)
    
    # Apply filters if provided
    if name:
        query = query.filter(Crop.name.ilike(f"%{name}%"))
    
    # Count total matching items
    total = query.count()
    
    # Apply pagination
    crops = query.offset((page - 1) * limit).limit(limit).all()
    
    # Calculate total pages
    pages = ceil(total / limit) if total > 0 else 1
    
    # Prepare response items
    items = []
    for crop in crops:
        try:
            base = str(request.base_url).rstrip('/')
            crop_dict = {
                "id": crop.id,
                "name": crop.name,
                "description": crop.description,
                "optimal_planting_time": crop.optimal_planting_time,
                "image_path": crop.image,
                "image_url": f"{base}{crop.image}" if crop.image else None
            }
            
            # Safely access complex JSON fields
            if hasattr(crop, 'climate_requirements') and crop.climate_requirements:
                crop_dict["climate_requirements"] = crop.climate_requirements
            
            if hasattr(crop, 'soil_requirements') and crop.soil_requirements:
                crop_dict["soil_requirements"] = crop.soil_requirements
                
            if hasattr(crop, 'risks') and crop.risks:
                crop_dict["risks"] = crop.risks
                
            items.append(crop_dict)
        except Exception as e:
            # Log the error but continue processing other crops
            print(f"Error processing crop {crop.id}: {str(e)}")
    
    return {
        "items": items,
        "total": total,
        "page": page,
        "pages": pages
    }


@router.get("/{crop_id}", response_model=CropResponse)
def get_crop(
    request: Request,
    crop_id: str = Path(..., description="The ID of the crop to retrieve"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific crop.
    """
    crop = db.query(Crop).filter(Crop.id == crop_id).first()
    if not crop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Crop not found"
        )
    base = str(request.base_url).rstrip('/')
    return {
        "id": crop.id,
        "name": crop.name,
        "description": crop.description,
        "optimal_planting_time": crop.optimal_planting_time,
        "climate_requirements": crop.climate_requirements,
        "soil_requirements": crop.soil_requirements,
        "risks": crop.risks,
        "image_path": crop.image,
        "image_url": f"{base}{crop.image}" if crop.image else None
    }


@router.get("/{crop_id}/market-data")
def get_crop_market_data(
    crop_id: str = Path(..., description="The ID of the crop"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get market data for a specific crop with proper error handling.
    """
    # Verify crop exists
    crop = db.query(Crop).filter(Crop.id == crop_id).first()
    if not crop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Crop not found"
        )
    
    # Get market data with fallback
    market_data = db.query(MarketPrice).filter(MarketPrice.crop_id == crop_id).first()
    
    if not market_data:
        # Return default data instead of error
        return {
            "crop_id": crop.id,
            "crop_name": crop.name,
            "current_price": 0.0,
            "price_trend": [],
            "percent_change": 0.0,
            "recommendation": "No market data available for this crop",
            "note": "This is default data as no market information exists"
        }
    
    # Safely create response
    try:
        response = {
            "crop_id": crop.id,
            "crop_name": crop.name,
            "current_price": market_data.current_price,
            "price_trend": market_data.price_trend or [],
            "percent_change": market_data.percent_change,
            "recommendation": market_data.recommendation or "No specific market recommendations available"
        }
        return response
    except Exception as e:
        # Handle unexpected errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing market data: {str(e)}"
        )


@router.get("/{crop_id}/recommendations")
def get_crop_recommendations(
    crop_id: str = Path(..., description="The ID of the crop"),
    farm_id: Optional[str] = Query(None, description="Optional farm ID for personalized recommendations"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get planting and care recommendations for a crop, optionally tailored to a specific farm.
    """
    # Verify crop exists and get data in one query
    crop = db.query(Crop).filter(Crop.id == crop_id).first()
    if not crop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Crop not found"
        )
    
    # Initialize default recommendations
    recommendations = {
        "planting": "No planting information available",
        "soil": "No soil information available",
        "market": "No market information available",
        "risks": "No risk information available"
    }
    
    # Get farm-specific recommendations if farm_id provided
    farm = None
    if farm_id:
        farm = db.query(Farm).filter(
            Farm.id == farm_id, 
            Farm.user_id == current_user.id
        ).first()
        
        if not farm:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Farm not found or you don't have access to this farm"
            )
    
    # Safely build recommendations
    try:
        # Planting recommendations
        if hasattr(crop, 'optimal_planting_time') and crop.optimal_planting_time:
            recommendations["planting"] = f"Optimal planting time is {crop.optimal_planting_time}"
        
        # Soil recommendations
        if hasattr(crop, 'soil_requirements') and isinstance(crop.soil_requirements, dict):
            soil_reqs = crop.soil_requirements
            ph_min = soil_reqs.get('ph_min', 'unknown')
            ph_max = soil_reqs.get('ph_max', 'unknown')
            
            if ph_min != 'unknown' and ph_max != 'unknown':
                recommendations["soil"] = f"Ensure soil pH is between {ph_min} and {ph_max}"
                
                # Add farm-specific advice if available
                if farm and hasattr(farm, 'soil_params') and isinstance(farm.soil_params, dict):
                    farm_soil_ph = farm.soil_params.get("ph")
                    if farm_soil_ph:
                        recommendations["soil"] += f". Your soil pH is {farm_soil_ph}."
                        
                        # Add advice if soil pH is out of range
                        try:
                            ph_val = float(farm_soil_ph)
                            min_val = float(ph_min)
                            max_val = float(ph_max)
                            
                            if ph_val < min_val:
                                recommendations["soil"] += " Your soil is too acidic for this crop. Consider adding lime to raise pH."
                            elif ph_val > max_val:
                                recommendations["soil"] += " Your soil is too alkaline for this crop. Consider adding sulfur to lower pH."
                            else:
                                recommendations["soil"] += " Your soil pH is suitable for this crop."
                        except (ValueError, TypeError):
                            # Handle non-numeric pH values
                            pass
            
            # Add more detailed soil recommendations if available
            soil_type = soil_reqs.get('soil_type')
            if soil_type:
                recommendations["soil"] += f" Preferred soil type: {soil_type}."
                
            # Nutrient requirements
            nutrients = []
            for nutrient in ['nitrogen', 'phosphorus', 'potassium']:
                if nutrient in soil_reqs:
                    nutrients.append(f"{nutrient.capitalize()}: {soil_reqs[nutrient]}")
            
            if nutrients:
                recommendations["soil"] += f" Nutrient requirements: {', '.join(nutrients)}."
        
        # Market recommendations
        market_data = db.query(MarketPrice).filter(MarketPrice.crop_id == crop_id).first()
        if market_data and hasattr(market_data, 'recommendation') and market_data.recommendation:
            recommendations["market"] = market_data.recommendation
        else:
            recommendations["market"] = "No specific market recommendations available for this crop."
            
            # Add price information if available
            if market_data and hasattr(market_data, 'current_price'):
                recommendations["market"] += f" Current market price: {market_data.current_price} per unit."
                
            if market_data and hasattr(market_data, 'percent_change'):
                change = market_data.percent_change
                direction = "up" if change > 0 else "down" if change < 0 else "unchanged"
                if direction != "unchanged":
                    recommendations["market"] += f" Price trend: {abs(change)}% {direction}."
        
        # Risk recommendations
        if hasattr(crop, 'risks') and isinstance(crop.risks, list) and crop.risks:
            risk_titles = []
            for risk in crop.risks:
                if isinstance(risk, dict) and 'title' in risk:
                    risk_titles.append(risk['title'])
            
            if risk_titles:
                recommendations["risks"] = "Common risks include: " + ", ".join(risk_titles)
                
                # Add first risk description for more detail
                if isinstance(crop.risks[0], dict) and 'description' in crop.risks[0]:
                    recommendations["risks"] += f". {crop.risks[0]['description']}"
    
    except Exception as e:
        # Log the error but return what we have
        print(f"Error generating recommendations for crop {crop_id}: {str(e)}")
        recommendations["error"] = "Some recommendations could not be generated due to data issues"
    
    return recommendations


# Additional endpoints for admin operations
@router.post("", response_model=CropResponse)
async def create_crop(
    request: Request,
    data: str = Form(...),
    file: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new crop.

    Expected JSON structure for `data` (stringified JSON) - example:

    {
      "name": "UploadCrop",
      "description": "Will upload image",
      "optimal_planting_time": "Now",
      "climate_requirements": {
        "temperature_min": 10.0,
        "temperature_max": 30.0,
        "rainfall_min": 100.0,
        "rainfall_max": 500.0,
        "humidity_min": 30.0,
        "humidity_max": 80.0,
        "growing_season": "90 days"
      },
      "soil_requirements": {
        "soil_type": "Loamy",
        "ph_min": 5.0,
        "ph_max": 7.0,
        "nitrogen": "Medium",
        "phosphorus": "Medium",
        "potassium": "Medium",
        "ec": "0.2",
        "salinity": "Low",
        "water_holding": "Medium",
        "organic_matter": "Medium"
      },
      "risks": [
        {"title": "Pests", "description": "Some pests", "severity": "Medium"}
      ]
    }

    Note: 'data' must contain the fields above as a JSON string. The endpoint still accepts an optional file in the same multipart request.
    """
    try:
        # Parse payload from required form 'data'
        try:
            payload = json.loads(data)
            crop_in = CropCreate.parse_obj(payload)
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid crop data: {e}")

        crop = Crop(
            name=crop_in.name,
            description=crop_in.description,
            optimal_planting_time=crop_in.optimal_planting_time,
            climate_requirements=crop_in.climate_requirements.dict(),
            soil_requirements=crop_in.soil_requirements.dict(),
            risks=[r.dict() for r in crop_in.risks]
        )
        db.add(crop)
        db.commit()
        db.refresh(crop)

        # If a file was provided in the same request, save it and update the crop
        if file:
            uploads_dir = LocalPath("uploads") / "crops"
            uploads_dir.mkdir(parents=True, exist_ok=True)

            safe_filename = f"{crop.id}_{file.filename}"
            file_path = uploads_dir / safe_filename

            contents = await file.read()
            with open(file_path, "wb") as f:
                f.write(contents)

            public_path = f"/uploads/crops/{safe_filename}"
            crop.image = public_path
            db.add(crop)
            db.commit()
            db.refresh(crop)

        base = str(request.base_url).rstrip('/')
        return {
            "id": crop.id,
            "name": crop.name,
            "description": crop.description,
            "optimal_planting_time": crop.optimal_planting_time,
            "climate_requirements": crop.climate_requirements,
            "soil_requirements": crop.soil_requirements,
            "risks": crop.risks,
            "image_path": crop.image,
            "image_url": f"{base}{crop.image}" if crop.image else None
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error creating crop: {e}")


@router.post("/{crop_id}/image", response_model=CropResponse)
async def upload_crop_image(
    crop_id: str,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload an image file for a crop (Admin only). Stores file under uploads/crops and sets crop.image to the public path."""
    crop = db.query(Crop).filter(Crop.id == crop_id).first()
    if not crop:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Crop not found")

    uploads_dir = LocalPath("uploads") / "crops"
    uploads_dir.mkdir(parents=True, exist_ok=True)

    safe_filename = f"{crop_id}_{file.filename}"
    file_path = uploads_dir / safe_filename

    try:
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)

        public_path = f"/uploads/crops/{safe_filename}"
        crop.image = public_path
        db.add(crop)
        db.commit()
        db.refresh(crop)
        return crop
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error uploading image: {e}")


@router.put("/{crop_id}", response_model=CropResponse)
def update_crop(
    crop_id: str,
    # This would need a CropUpdate schema that we haven't implemented yet
    # crop_data: CropUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update an existing crop (Admin only).
    Note: This endpoint is a placeholder and would need a proper implementation.
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Crop update not implemented yet"
    )


@router.delete("/{crop_id}")
def delete_crop(
    crop_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a crop (Admin only).
    Note: This endpoint is a placeholder and would need a proper implementation.
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Crop deletion not implemented yet"
    ) 