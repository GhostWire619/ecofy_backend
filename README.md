# Ecofy Backend API

A robust FastAPI backend for the Ecofy agricultural management platform.

## Features

- Authentication and user management
- Farm management with soil data tracking
- Crop information and recommendations
- Market price monitoring and trends
- Marketplace for agricultural products
- Order processing
- Chat functionality with Gemini AI integration
- Weather and satellite data integration
- Notifications system

## Technology Stack

- **FastAPI**: Modern, fast web framework for building APIs
- **SQLAlchemy**: SQL toolkit and ORM
- **Pydantic**: Data validation and settings management
- **JWT**: Token-based authentication
- **SQLite**: Database (can be switched to PostgreSQL for production)
- **Gemini AI**: Google's generative AI for intelligent chat responses

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
   GOOGLE_API_KEY=your_gemini_api_key
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

**Example (JavaScript):**

```javascript
// Register a new user
async function registerUser(userData) {
  try {
    const response = await fetch("http://localhost:8000/api/v1/auth/register", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(userData),
    });

    if (!response.ok) {
      throw new Error(`Error: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Registration failed:", error);
    throw error;
  }
}

// Usage
const newUser = {
  email: "user@example.com",
  full_name: "John Doe",
  password: "secure_password",
  phone_number: "+1234567890",
  location: "New York",
  preferred_language: "en",
};

registerUser(newUser)
  .then((user) => console.log("User registered:", user))
  .catch((error) => console.error(error));
```

**Example (cURL):**

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "full_name": "John Doe",
    "password": "secure_password",
    "phone_number": "+1234567890",
    "location": "New York",
    "preferred_language": "en"
  }'
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

**Example (JavaScript):**

```javascript
// Login user
async function loginUser(email, password) {
  try {
    const response = await fetch("http://localhost:8000/api/v1/auth/login", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        username: email, // Note: API uses 'username' field for email
        password: password,
      }),
    });

    if (!response.ok) {
      throw new Error(`Error: ${response.status}`);
    }

    const data = await response.json();
    // Store token in localStorage for later use
    localStorage.setItem("token", data.access_token);
    return data;
  } catch (error) {
    console.error("Login failed:", error);
    throw error;
  }
}

// Usage
loginUser("user@example.com", "secure_password")
  .then((data) => console.log("Login successful:", data))
  .catch((error) => console.error(error));
```

**Example (cURL):**

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "user@example.com",
    "password": "secure_password"
  }'
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

**Example (JavaScript):**

```javascript
// Refresh token
async function refreshToken(token) {
  try {
    const response = await fetch("http://localhost:8000/api/v1/auth/refresh", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ token }),
    });

    if (!response.ok) {
      throw new Error(`Error: ${response.status}`);
    }

    const data = await response.json();
    // Update token in localStorage
    localStorage.setItem("token", data.access_token);
    return data;
  } catch (error) {
    console.error("Token refresh failed:", error);
    throw error;
  }
}

// Usage
const currentToken = localStorage.getItem("token");
refreshToken(currentToken)
  .then((data) => console.log("Token refreshed:", data))
  .catch((error) => console.error(error));
```

**Example (cURL):**

```bash
curl -X POST http://localhost:8000/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }'
```

#### POST `/api/v1/auth/logout`

Logout a user (client-side token removal).

**Response:**

```json
{
  "success": true
}
```

**Example (JavaScript):**

```javascript
// Logout user
async function logoutUser() {
  try {
    const token = localStorage.getItem("token");

    const response = await fetch("http://localhost:8000/api/v1/auth/logout", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
    });

    // Remove token from localStorage regardless of response
    localStorage.removeItem("token");

    if (!response.ok) {
      throw new Error(`Error: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error("Logout failed:", error);
    // Still remove token even if API call fails
    localStorage.removeItem("token");
    throw error;
  }
}

// Usage
logoutUser()
  .then((data) => console.log("Logout successful:", data))
  .catch((error) => console.error(error));
```

**Example (cURL):**

```bash
curl -X POST http://localhost:8000/api/v1/auth/logout \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
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

**Example (JavaScript):**

```javascript
// Get current user profile
async function getCurrentUser() {
  try {
    const token = localStorage.getItem("token");

    const response = await fetch("http://localhost:8000/api/v1/users/me", {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      throw new Error(`Error: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error("Failed to get user profile:", error);
    throw error;
  }
}

// Usage
getCurrentUser()
  .then((user) => console.log("User profile:", user))
  .catch((error) => console.error(error));
```

**Example (cURL):**

```bash
curl -X GET http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
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

**Example (JavaScript):**

```javascript
// Update user profile
async function updateUserProfile(userData) {
  try {
    const token = localStorage.getItem("token");

    const response = await fetch("http://localhost:8000/api/v1/users/me", {
      method: "PUT",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(userData),
    });

    if (!response.ok) {
      throw new Error(`Error: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error("Failed to update user profile:", error);
    throw error;
  }
}

// Usage
const updatedUserData = {
  full_name: "John Smith",
  phone_number: "+1234567890",
  location: "Los Angeles",
  preferred_language: "en",
};

updateUserProfile(updatedUserData)
  .then((user) => console.log("Profile updated:", user))
  .catch((error) => console.error(error));
```

**Example (cURL):**

```bash
curl -X PUT http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "John Smith",
    "phone_number": "+1234567890",
    "location": "Los Angeles",
    "preferred_language": "en"
  }'
```

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

**Example (JavaScript):**

```javascript
// Update user language preference
async function updateLanguage(language) {
  try {
    const token = localStorage.getItem("token");

    const response = await fetch(
      "http://localhost:8000/api/v1/users/language",
      {
        method: "PATCH",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ preferred_language: language }),
      }
    );

    if (!response.ok) {
      throw new Error(`Error: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error("Failed to update language:", error);
    throw error;
  }
}

// Usage
updateLanguage("fr")
  .then((result) => console.log("Language updated:", result))
  .catch((error) => console.error(error));
```

**Example (cURL):**

```bash
curl -X PATCH http://localhost:8000/api/v1/users/language \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "preferred_language": "fr"
  }'
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

**Example (JavaScript):**

```javascript
// Get all farms for current user
async function getUserFarms() {
  try {
    const token = localStorage.getItem("token");

    const response = await fetch("http://localhost:8000/api/v1/farms", {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      throw new Error(`Error: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error("Failed to get farms:", error);
    throw error;
  }
}

// Usage
getUserFarms()
  .then((farms) => {
    console.log("User farms:", farms);
    // Display farms in UI
    farms.forEach((farm) => {
      console.log(`Farm: ${farm.name}, Size: ${farm.size} hectares`);
    });
  })
  .catch((error) => console.error(error));
```

**Example (cURL):**

```bash
curl -X GET http://localhost:8000/api/v1/farms \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
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

**Example (JavaScript):**

```javascript
// Create a new farm
async function createFarm(farmData) {
  try {
    const token = localStorage.getItem("token");

    const response = await fetch("http://localhost:8000/api/v1/farms", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(farmData),
    });

    if (!response.ok) {
      throw new Error(`Error: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error("Failed to create farm:", error);
    throw error;
  }
}

// Usage
const newFarm = {
  name: "Organic Valley Farm",
  location: "Countryside",
  size: 85.7,
  topography: "hilly",
  coordinates: {
    latitude: 40.7128,
    longitude: -74.006,
  },
  soil_params: {
    ph: 6.2,
    nitrogen: 0.4,
    phosphorus: 0.3,
    potassium: 0.5,
    organic_matter: 4.1,
  },
};

createFarm(newFarm)
  .then((farm) => console.log("Farm created:", farm))
  .catch((error) => console.error(error));
```

**Example (cURL):**

```bash
curl -X POST http://localhost:8000/api/v1/farms \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Organic Valley Farm",
    "location": "Countryside",
    "size": 85.7,
    "topography": "hilly",
    "coordinates": {
      "latitude": 40.7128,
      "longitude": -74.006
    },
    "soil_params": {
      "ph": 6.2,
      "nitrogen": 0.4,
      "phosphorus": 0.3,
      "potassium": 0.5,
      "organic_matter": 4.1
    }
  }'
```

#### GET `/api/v1/farms/{farm_id}`

Get a specific farm by ID.

**Headers:**

- Authorization: Bearer {token}

**Response:** Farm object.

**Example (JavaScript):**

```javascript
// Get farm by ID
async function getFarmById(farmId) {
  try {
    const token = localStorage.getItem("token");

    const response = await fetch(
      `http://localhost:8000/api/v1/farms/${farmId}`,
      {
        method: "GET",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );

    if (!response.ok) {
      throw new Error(`Error: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error("Failed to get farm:", error);
    throw error;
  }
}

// Usage
getFarmById("farm_id")
  .then((farm) => console.log("Farm details:", farm))
  .catch((error) => console.error(error));
```

**Example (cURL):**

```bash
curl -X GET http://localhost:8000/api/v1/farms/farm_id \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

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

## Frontend Integration Utilities

Below are some utility functions to help frontend developers quickly integrate with the Ecofy API:

### API Client Setup

```javascript
// api.js - A simple API client for Ecofy

class EcofyAPI {
  constructor(baseURL = "http://localhost:8000/api/v1") {
    this.baseURL = baseURL;
    this.token = localStorage.getItem("token") || null;
  }

  // Set authentication token
  setToken(token) {
    this.token = token;
    localStorage.setItem("token", token);
  }

  // Clear authentication token
  clearToken() {
    this.token = null;
    localStorage.removeItem("token");
  }

  // Get authentication headers
  getHeaders(includeContentType = true) {
    const headers = {};

    if (this.token) {
      headers["Authorization"] = `Bearer ${this.token}`;
    }

    if (includeContentType) {
      headers["Content-Type"] = "application/json";
    }

    return headers;
  }

  // Generic request method
  async request(endpoint, method = "GET", data = null, customHeaders = {}) {
    const url = `${this.baseURL}${endpoint}`;

    const options = {
      method,
      headers: {
        ...this.getHeaders(),
        ...customHeaders,
      },
    };

    if (data && method !== "GET") {
      options.body = JSON.stringify(data);
    }

    try {
      const response = await fetch(url, options);

      // Handle token expiration
      if (response.status === 401) {
        this.clearToken();
        throw new Error("Authentication failed - please login again");
      }

      // Parse JSON response if present
      let result;
      const contentType = response.headers.get("content-type");
      if (contentType && contentType.includes("application/json")) {
        result = await response.json();
      } else {
        result = await response.text();
      }

      if (!response.ok) {
        throw new Error(result.detail || `API Error: ${response.status}`);
      }

      return result;
    } catch (error) {
      console.error(`API request failed: ${error.message}`);
      throw error;
    }
  }

  // Authentication methods
  async register(userData) {
    return this.request("/auth/register", "POST", userData);
  }

  async login(email, password) {
    const result = await this.request("/auth/login", "POST", {
      username: email, // API expects 'username' for email
      password,
    });

    if (result.access_token) {
      this.setToken(result.access_token);
    }

    return result;
  }

  async logout() {
    try {
      await this.request("/auth/logout", "POST");
    } finally {
      this.clearToken();
    }
  }

  // User methods
  async getCurrentUser() {
    return this.request("/users/me");
  }

  async updateUserProfile(userData) {
    return this.request("/users/me", "PUT", userData);
  }

  // Farm methods
  async getFarms() {
    return this.request("/farms");
  }

  async getFarm(farmId) {
    return this.request(`/farms/${farmId}`);
  }

  async createFarm(farmData) {
    return this.request("/farms", "POST", farmData);
  }

  async updateFarm(farmId, farmData) {
    return this.request(`/farms/${farmId}`, "PUT", farmData);
  }

  async deleteFarm(farmId) {
    return this.request(`/farms/${farmId}`, "DELETE");
  }

  // File upload example
  async uploadFarmImage(farmId, fileData) {
    const formData = new FormData();
    formData.append("file", fileData);

    return this.request(
      `/farms/${farmId}/image`,
      "POST",
      formData,
      { "Content-Type": undefined } // Let browser set correct content type with boundary
    );
  }

  // Add more methods for other endpoints as needed
}

// Usage example
const api = new EcofyAPI();

// Login example
async function loginExample() {
  try {
    const result = await api.login("user@example.com", "password");
    console.log("Logged in as:", result.user.full_name);
    return result;
  } catch (error) {
    console.error("Login failed:", error.message);
  }
}

// Create farm example
async function createFarmExample() {
  try {
    const farm = await api.createFarm({
      name: "New Farm",
      location: "Rural Area",
      size: 120.5,
      // other farm properties
    });
    console.log("Farm created:", farm);
    return farm;
  } catch (error) {
    console.error("Failed to create farm:", error.message);
  }
}
```

### React Hooks Example

```javascript
// useEcofyApi.js - React hook for API integration

import { useState, useEffect, useCallback } from "react";

// Import the API client from above
// import { EcofyAPI } from './api';

function useEcofyApi() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  const api = new EcofyAPI();

  // Check if user is authenticated on hook mount
  useEffect(() => {
    const token = localStorage.getItem("token");
    if (token) {
      setIsAuthenticated(true);
      fetchCurrentUser();
    }
  }, []);

  // Fetch current user profile
  const fetchCurrentUser = useCallback(async () => {
    if (!isAuthenticated) return;

    setLoading(true);
    try {
      const userData = await api.getCurrentUser();
      setUser(userData);
      setError(null);
    } catch (err) {
      setError(err.message);
      setIsAuthenticated(false);
      api.clearToken();
    } finally {
      setLoading(false);
    }
  }, [isAuthenticated]);

  // Login handler
  const login = useCallback(async (email, password) => {
    setLoading(true);
    try {
      const result = await api.login(email, password);
      setUser(result.user);
      setIsAuthenticated(true);
      setError(null);
      return result;
    } catch (err) {
      setError(err.message);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  // Logout handler
  const logout = useCallback(async () => {
    setLoading(true);
    try {
      await api.logout();
    } catch (err) {
      console.error("Logout error:", err);
    } finally {
      setUser(null);
      setIsAuthenticated(false);
      setLoading(false);
    }
  }, []);

  return {
    user,
    loading,
    error,
    isAuthenticated,
    api,
    login,
    logout,
    fetchCurrentUser,
  };
}

export default useEcofyApi;
```

### Example with React Component

```jsx
// FarmsList.jsx - Example component using the API hook

import React, { useEffect, useState } from "react";
import useEcofyApi from "./useEcofyApi";

function FarmsList() {
  const { api, isAuthenticated, loading: authLoading } = useEcofyApi();
  const [farms, setFarms] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (isAuthenticated) {
      fetchFarms();
    }
  }, [isAuthenticated]);

  const fetchFarms = async () => {
    setLoading(true);
    try {
      const farmsData = await api.getFarms();
      setFarms(farmsData);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (authLoading || loading) {
    return <div>Loading...</div>;
  }

  if (error) {
    return <div>Error: {error}</div>;
  }

  if (!isAuthenticated) {
    return <div>Please log in to view your farms.</div>;
  }

  return (
    <div>
      <h2>Your Farms</h2>
      {farms.length === 0 ? (
        <p>You don't have any farms yet.</p>
      ) : (
        <ul>
          {farms.map((farm) => (
            <li key={farm.id}>
              <h3>{farm.name}</h3>
              <p>Location: {farm.location}</p>
              <p>Size: {farm.size} hectares</p>
            </li>
          ))}
        </ul>
      )}
      <button onClick={fetchFarms}>Refresh</button>
    </div>
  );
}

export default FarmsList;
```
