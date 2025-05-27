# Ecofy Backend API

A robust FastAPI backend for the Ecofy agricultural management platform.

## Features

- Authentication and user management
- Farm management with soil data tracking
- Crop information and recommendations
- Market price monitoring and trends
- Marketplace for agricultural products
- Order processing
- Chat functionality
- Weather and satellite data integration
- Notifications system

## Technology Stack

- **FastAPI**: Modern, fast web framework for building APIs
- **SQLAlchemy**: SQL toolkit and ORM
- **Pydantic**: Data validation and settings management
- **JWT**: Token-based authentication
- **SQLite**: Database (can be switched to PostgreSQL for production)

## Setup Instructions

1. **Clone the repository**

   ```
   git clone https://github.com/yourusername/ecofy_backend.git
   cd ecofy_backend
   ```

2. **Create a virtual environment**

   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**

   ```
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the project root with the following:

   ```
   SECRET_KEY=your_secret_key
   DATABASE_URL=sqlite:///./ecofy.db
   WEATHER_API_KEY=your_weather_api_key
   SATELLITE_API_KEY=your_satellite_api_key
   ```

5. **Run the application**

   ```
   uvicorn app.main:app --reload
   ```

6. **Access the API**
   - API Endpoints: `http://localhost:8000/api/`
   - API Documentation: `http://localhost:8000/docs`

## API Endpoints

The API is organized into several modules:

- **Authentication**: `/api/auth/` - Register, login, token refresh
- **Users**: `/api/users/` - User profile management
- **Farms**: `/api/farms/` - Farm management
- **Crops**: `/api/crops/` - Crop information and recommendations
- **Market**: `/api/market/` - Market price data
- **Marketplace**: `/api/marketplace/` - Product listing and management
- **Orders**: `/api/orders/` - Order processing
- **Notifications**: `/api/notifications/` - User notifications
- **Chat**: `/api/chat/` - Chat functionality
- **Weather**: `/api/weather/` - Weather forecasts
- **Satellite**: `/api/satellite/` - Satellite soil data

## Development

### Database Migrations

This project uses Alembic for database migrations:

```
# Generate migration
alembic revision --autogenerate -m "description"

# Apply migration
alembic upgrade head
```

### Testing

Run tests with pytest:

```
pytest
```

## License

MIT
