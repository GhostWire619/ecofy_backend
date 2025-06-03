from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import logging
import sys

from app.api.routes import auth, users, farms, crops, market, marketplace, orders, notifications, chat, external
from app.core.config import settings
from app.database import engine, Base

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# Get logger for this file
logger = logging.getLogger(__name__)
logger.info("Starting Ecofy API")

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set up CORS
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Include API routes
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["Authentication"])
app.include_router(users.router, prefix=f"{settings.API_V1_STR}/users", tags=["Users"])
app.include_router(farms.router, prefix=f"{settings.API_V1_STR}/farms", tags=["Farms"])
app.include_router(crops.router, prefix=f"{settings.API_V1_STR}/crops", tags=["Crops"])
app.include_router(market.router, prefix=f"{settings.API_V1_STR}/market", tags=["Market"])
app.include_router(marketplace.router, prefix=f"{settings.API_V1_STR}/marketplace", tags=["Marketplace"])
app.include_router(orders.router, prefix=f"{settings.API_V1_STR}/orders", tags=["Orders"])
app.include_router(notifications.router, prefix=f"{settings.API_V1_STR}/notifications", tags=["Notifications"])
app.include_router(chat.router, prefix=f"{settings.API_V1_STR}/chat", tags=["Chat"])
app.include_router(external.router, prefix=f"{settings.API_V1_STR}", tags=["External"])

@app.get("/", tags=["Root"])
async def root():
    return {"message": "Welcome to Ecofy API. Visit /docs for API documentation."}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True) 