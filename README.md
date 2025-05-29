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

## API Documentation for Frontend Developers

All API endpoints are prefixed with `/api/v1`.

### Authentication

#### POST `/api/v1/auth/register`

Register a new user.

**Request Body:**

```json
{
  "email": "user@example.com",
  "full_name": "John Doe",
  "password": "secure_password",
  "phone_number": "+1234567890",
  "location": "New York",
  "preferred_language": "en"
}
```

**Response:**

```json
{
  "id": "user_id",
  "email": "user@example.com",
  "full_name": "John Doe",
  "phone_number": "+1234567890",
  "location": "New York",
  "preferred_language": "en",
  "is_active": true
}
```

#### POST `/api/v1/auth/login`

Authenticate a user and get access token.

**Request Body:**

```json
{
  "username": "user@example.com", // Email is used as username
  "password": "secure_password"
}
```

**Response:**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "user_id",
    "email": "user@example.com",
    "full_name": "John Doe"
    // other user fields
  }
}
```

#### POST `/api/v1/auth/refresh`

Refresh an access token.

**Request Body:**

```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response:** Same as login response.

#### POST `/api/v1/auth/logout`

Logout a user (client-side token removal).

**Response:**

```json
{
  "success": true
}
```

### Users

#### GET `/api/v1/users/me`

Get current user information.

**Headers:**

- Authorization: Bearer {token}

**Response:**

```json
{
  "id": "user_id",
  "email": "user@example.com",
  "full_name": "John Doe",
  "phone_number": "+1234567890",
  "location": "New York",
  "preferred_language": "en",
  "is_active": true
}
```

#### PUT `/api/v1/users/me`

Update current user information.

**Headers:**

- Authorization: Bearer {token}

**Request Body:**

```json
{
  "full_name": "John Doe",
  "phone_number": "+1234567890",
  "location": "New York",
  "preferred_language": "en"
}
```

**Response:** Updated user object.

#### PATCH `/api/v1/users/language`

Update user's preferred language.

**Headers:**

- Authorization: Bearer {token}

**Request Body:**

```json
{
  "preferred_language": "fr"
}
```

**Response:**

```json
{
  "success": true,
  "preferred_language": "fr"
}
```

### Farms

#### GET `/api/v1/farms`

Get all farms for the current user.

**Headers:**

- Authorization: Bearer {token}

**Response:**

```json
[
  {
    "id": "farm_id",
    "name": "Main Farm",
    "location": "Countryside",
    "size": 100.5,
    "topography": "flat",
    "coordinates": {
      "latitude": 40.7128,
      "longitude": -74.006
    },
    "soil_params": {
      "ph": 6.5,
      "nitrogen": 0.3,
      "phosphorus": 0.2,
      "potassium": 0.4,
      "organic_matter": 3.2
    },
    "crop_history": [],
    "image": null,
    "user_id": "user_id"
  }
]
```

#### POST `/api/v1/farms`

Create a new farm.

**Headers:**

- Authorization: Bearer {token}

**Request Body:**

```json
{
  "name": "Main Farm",
  "location": "Countryside",
  "size": 100.5,
  "topography": "flat",
  "coordinates": {
    "latitude": 40.7128,
    "longitude": -74.006
  },
  "soil_params": {
    "ph": 6.5,
    "nitrogen": 0.3,
    "phosphorus": 0.2,
    "potassium": 0.4,
    "organic_matter": 3.2
  }
}
```

**Response:** Created farm object.

#### GET `/api/v1/farms/{farm_id}`

Get a specific farm by ID.

**Headers:**

- Authorization: Bearer {token}

**Response:** Farm object.

#### PUT `/api/v1/farms/{farm_id}`

Update a farm.

**Headers:**

- Authorization: Bearer {token}

**Request Body:** Same as create farm.

**Response:** Updated farm object.

#### DELETE `/api/v1/farms/{farm_id}`

Delete a farm.

**Headers:**

- Authorization: Bearer {token}

**Response:**

```json
{
  "success": true
}
```

#### POST `/api/v1/farms/{farm_id}/crop-history`

Add crop history to a farm.

**Headers:**

- Authorization: Bearer {token}

**Request Body:**

```json
{
  "crop_name": "Corn",
  "start_date": "2023-01-01",
  "end_date": "2023-06-30",
  "yield": 5.2,
  "notes": "Good harvest despite drought"
}
```

**Response:** Updated farm object.

#### POST `/api/v1/farms/{farm_id}/image`

Upload an image for a farm.

**Headers:**

- Authorization: Bearer {token}

**Request Body:** Form data with file upload.

**Response:**

```json
{
  "image_url": "/uploads/farms/farm_id/image.jpg"
}
```

### Crops

#### GET `/api/v1/crops`

Get a list of all available crops.

**Headers:**

- Authorization: Bearer {token}

**Response:**

```json
[
  {
    "id": "crop_id",
    "name": "Corn",
    "scientific_name": "Zea mays",
    "description": "...",
    "growing_season": ["Spring", "Summer"],
    "optimal_conditions": {
      "temperature": { "min": 20, "max": 30 },
      "soil_ph": { "min": 5.8, "max": 7.0 },
      "water_needs": "medium"
    }
  }
]
```

#### GET `/api/v1/crops/{crop_id}`

Get detailed information about a specific crop.

**Headers:**

- Authorization: Bearer {token}

**Response:** Detailed crop object.

#### GET `/api/v1/crops/recommendations`

Get crop recommendations based on soil parameters and location.

**Headers:**

- Authorization: Bearer {token}

**Query Parameters:**

- farm_id (optional): Get recommendations for a specific farm

**Response:**

```json
{
  "recommended_crops": [
    {
      "crop_id": "crop_id",
      "name": "Corn",
      "suitability_score": 0.85,
      "reason": "Good soil pH and climate match"
    }
  ]
}
```

### Market

#### GET `/api/v1/market/prices`

Get current market prices for agricultural products.

**Headers:**

- Authorization: Bearer {token}

**Query Parameters:**

- product_type (optional): Filter by product type

**Response:**

```json
[
  {
    "product": "Corn",
    "price_per_unit": 5.2,
    "unit": "kg",
    "updated_at": "2023-06-15T10:30:00Z"
  }
]
```

#### GET `/api/v1/market/trends`

Get market price trends over time.

**Headers:**

- Authorization: Bearer {token}

**Query Parameters:**

- product: Product name
- period: Time period (week, month, year)

**Response:**

```json
{
  "product": "Corn",
  "period": "month",
  "data_points": [
    { "date": "2023-05-01", "price": 5.1 },
    { "date": "2023-05-15", "price": 5.15 },
    { "date": "2023-06-01", "price": 5.2 }
  ]
}
```

### Marketplace

#### GET `/api/v1/marketplace/products`

Get all products available in the marketplace.

**Headers:**

- Authorization: Bearer {token}

**Query Parameters:**

- category (optional): Filter by category
- search (optional): Search term

**Response:**

```json
[
  {
    "id": "product_id",
    "title": "Organic Corn",
    "description": "Freshly harvested organic corn",
    "price": 6.5,
    "unit": "kg",
    "quantity_available": 500,
    "seller": {
      "id": "user_id",
      "name": "John Doe"
    },
    "images": ["url1", "url2"],
    "created_at": "2023-06-01T10:00:00Z"
  }
]
```

#### POST `/api/v1/marketplace/products`

List a new product for sale.

**Headers:**

- Authorization: Bearer {token}

**Request Body:**

```json
{
  "title": "Organic Corn",
  "description": "Freshly harvested organic corn",
  "price": 6.5,
  "unit": "kg",
  "quantity_available": 500,
  "category": "Grain",
  "farm_id": "farm_id"
}
```

**Response:** Created product object.

#### GET `/api/v1/marketplace/products/{product_id}`

Get details of a specific product.

**Headers:**

- Authorization: Bearer {token}

**Response:** Detailed product object.

### Orders

#### GET `/api/v1/orders`

Get all orders for the current user.

**Headers:**

- Authorization: Bearer {token}

**Query Parameters:**

- type (optional): "buying" or "selling"
- status (optional): Order status

**Response:**

```json
[
  {
    "id": "order_id",
    "product_id": "product_id",
    "product_title": "Organic Corn",
    "quantity": 50,
    "price_per_unit": 6.5,
    "total_price": 325.0,
    "status": "pending",
    "buyer_id": "user_id",
    "seller_id": "seller_id",
    "created_at": "2023-06-10T14:30:00Z"
  }
]
```

#### POST `/api/v1/orders`

Create a new order.

**Headers:**

- Authorization: Bearer {token}

**Request Body:**

```json
{
  "product_id": "product_id",
  "quantity": 50
}
```

**Response:** Created order object.

#### GET `/api/v1/orders/{order_id}`

Get details of a specific order.

**Headers:**

- Authorization: Bearer {token}

**Response:** Detailed order object.

### Notifications

#### GET `/api/v1/notifications`

Get all notifications for the current user.

**Headers:**

- Authorization: Bearer {token}

**Response:**

```json
[
  {
    "id": "notification_id",
    "type": "order_update",
    "message": "Your order has been shipped",
    "is_read": false,
    "created_at": "2023-06-12T09:45:00Z",
    "data": {
      "order_id": "order_id"
    }
  }
]
```

#### PATCH `/api/v1/notifications/{notification_id}/read`

Mark a notification as read.

**Headers:**

- Authorization: Bearer {token}

**Response:**

```json
{
  "success": true
}
```

### Chat

#### GET `/api/v1/chat/conversations`

Get all chat conversations for the current user.

**Headers:**

- Authorization: Bearer {token}

**Response:**

```json
[
  {
    "id": "conversation_id",
    "with_user": {
      "id": "user_id",
      "name": "Jane Smith"
    },
    "last_message": "When will the corn be available?",
    "unread_count": 2,
    "updated_at": "2023-06-13T15:20:00Z"
  }
]
```

#### GET `/api/v1/chat/messages/{conversation_id}`

Get messages for a specific conversation.

**Headers:**

- Authorization: Bearer {token}

**Response:**

```json
{
  "conversation_id": "conversation_id",
  "messages": [
    {
      "id": "message_id",
      "sender_id": "user_id",
      "content": "When will the corn be available?",
      "created_at": "2023-06-13T15:20:00Z",
      "is_read": true
    }
  ]
}
```

#### POST `/api/v1/chat/messages`

Send a new chat message.

**Headers:**

- Authorization: Bearer {token}

**Request Body:**

```json
{
  "conversation_id": "conversation_id",
  "content": "The corn will be available next week"
}
```

**Response:** Created message object.

### External APIs

#### GET `/api/v1/weather`

Get weather data for a specific location.

**Headers:**

- Authorization: Bearer {token}

**Query Parameters:**

- latitude: Latitude coordinate
- longitude: Longitude coordinate
- days (optional): Number of forecast days (default: 7)

**Response:**

```json
{
  "location": {
    "name": "New York",
    "latitude": 40.7128,
    "longitude": -74.006
  },
  "current": {
    "temperature": 25.3,
    "humidity": 65,
    "wind_speed": 12,
    "precipitation": 0,
    "condition": "sunny"
  },
  "forecast": [
    {
      "date": "2023-06-16",
      "temperature": { "min": 22, "max": 28 },
      "precipitation_chance": 10,
      "condition": "partly cloudy"
    }
  ]
}
```

#### GET `/api/v1/satellite`

Get satellite imagery and soil data.

**Headers:**

- Authorization: Bearer {token}

**Query Parameters:**

- farm_id: ID of the farm

**Response:**

```json
{
  "farm_id": "farm_id",
  "imagery_url": "https://example.com/satellite/image.jpg",
  "ndvi_index": 0.75,
  "soil_moisture": 45,
  "analysis": {
    "crop_health": "good",
    "problem_areas": [
      {
        "coordinates": { "latitude": 40.713, "longitude": -74.0062 },
        "issue": "possible water stress"
      }
    ]
  },
  "captured_at": "2023-06-01T00:00:00Z"
}
```

## Authentication

All endpoints except for authentication require a valid JWT token. Include it in the Authorization header:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## Error Handling

The API returns standard HTTP status codes:

- 200: Success
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 500: Internal Server Error

Error responses include a detail message:

```json
{
  "detail": "Error message"
}
```

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
