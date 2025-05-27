from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from app.api.deps import get_current_user
from app.database import get_db
from app.models.crop import Crop
from app.models.market import MarketPrice
from app.models.user import User
from app.schemas.market import MarketData, MarketDataResponse, PricePoint

router = APIRouter()

@router.get("/prices", response_model=MarketDataResponse)
def get_market_prices(
    crop_id: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(MarketPrice)
    
    if crop_id:
        query = query.filter(MarketPrice.crop_id == crop_id)
        
    market_prices = query.all()
    
    data = []
    for price in market_prices:
        crop = db.query(Crop).filter(Crop.id == price.crop_id).first()
        if crop:
            data.append(
                MarketData(
                    crop_id=crop.id,
                    crop_name=crop.name,
                    current_price=price.current_price,
                    price_trend=price.price_trend,
                    percent_change=price.percent_change,
                    recommendation=price.recommendation
                )
            )
    
    return MarketDataResponse(data=data)


@router.get("/trends", response_model=List[PricePoint])
def get_market_trends(
    crop_id: str,
    period: str = Query("month", enum=["week", "month", "year"]),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Check if crop exists
    crop = db.query(Crop).filter(Crop.id == crop_id).first()
    if not crop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Crop not found"
        )
    
    # Get market data
    market_data = db.query(MarketPrice).filter(MarketPrice.crop_id == crop_id).first()
    if not market_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Market data not found for this crop"
        )
    
    # In a real app, we would filter the price trend based on the period
    # For demo purposes, we'll return all price points
    price_trend = market_data.price_trend
    
    # Filter based on period if needed
    if period == "week":
        week_ago = datetime.utcnow() - timedelta(days=7)
        return [point for point in price_trend if datetime.fromisoformat(point["date"]) >= week_ago]
    elif period == "month":
        month_ago = datetime.utcnow() - timedelta(days=30)
        return [point for point in price_trend if datetime.fromisoformat(point["date"]) >= month_ago]
    
    return price_trend 