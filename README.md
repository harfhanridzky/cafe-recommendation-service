# Cafe Recommendation Service

A FastAPI-based microservice for discovering and getting personalized cafe recommendations using Google Places API.

## System Overview

This service provides two main capabilities:
1. **Search**: Find cafes near your current location
2. **Recommend**: Get filtered and ranked cafe recommendations based on rating and price preferences

### Key Features
- Real-time cafe data from Google Places API
- Distance calculation using Haversine formula
- Smart filtering by rating and price range
- Ranking by highest rating and nearest distance
- No database or persistence layer - all data fetched on-demand
- Clean separation of concerns using Domain-Driven Design

## Architecture

The service follows Domain-Driven Design with three bounded contexts:

### BC1 (Catalog) - Domain Layer
- **Purpose**: Maps Google Places API data to internal domain entities
- **Components**: `Cafe`, `Location`, `Rating`, `PriceRange`
- **Location**: `app/domain/models.py`

### BC2 (Search) - Search Service
- **Purpose**: Orchestrates cafe search operations
- **Responsibilities**:
  - Calls Google Places API
  - Maps external data to domain entities
  - Calculates distances from user location
- **Location**: `app/services/search_service.py`

### BC3 (Recommendation) - Recommendation Service
- **Purpose**: Applies business logic for filtering and ranking
- **Responsibilities**:
  - Filters by minimum rating
  - Filters by price range
  - Sorts by rating (descending) then distance (ascending)
  - Applies result limits
- **Location**: `app/services/recommendation_service.py`

## Project Structure

```
TST_Tubes_Implementation/
├── app/
│   ├── __init__.py
│   ├── main.py                              # FastAPI application entry point
│   ├── config.py                            # Configuration and settings
│   ├── domain/                              # BC1: Domain models
│   │   ├── __init__.py
│   │   └── models.py                        # Cafe, Location, Rating, PriceRange
│   ├── infrastructure/                      # External API integration
│   │   ├── __init__.py
│   │   └── google_places_client.py          # Google Places API wrapper
│   ├── services/                            # Business logic
│   │   ├── __init__.py
│   │   ├── search_service.py                # BC2: Search orchestration
│   │   └── recommendation_service.py        # BC3: Filtering & ranking
│   ├── api/                                 # API layer
│   │   ├── __init__.py
│   │   └── routers/
│   │       ├── __init__.py
│   │       ├── search.py                    # /api/v1/search endpoint
│   │       └── recommendations.py           # /api/v1/recommendations endpoint
│   └── schemas/                             # Pydantic models
│       ├── __init__.py
│       └── responses.py                     # API response schemas
├── .env                                     # Environment variables (create from .env.example)
├── .env.example                             # Example environment file
├── requirements.txt                         # Python dependencies
└── README.md                                # This file
```

## Domain Model

### Entity: Cafe
```python
Cafe {
    id: str                    # Google place_id
    name: str                  # Cafe name
    address: str               # Full address
    location: Location         # Geographic coordinates
    rating: Rating             # Rating value object (0.0-5.0)
    price_range: PriceRange    # Price category enum
    distance_meters: float?    # Distance from search center
}
```

### Value Object: Location
```python
Location {
    latitude: float            # -90 to 90
    longitude: float           # -180 to 180
}
```

### Value Object: Rating
```python
Rating {
    value: float              # 0.0 to 5.0
}
```

### Enum: PriceRange
Maps from Google's `price_level` (0-4):
- `0` → `CHEAP`
- `1` → `MEDIUM`
- `2` → `HIGH`
- `3` → `VERY_HIGH`
- `4` → `LUXURY`
- `None` → `UNKNOWN`

## Setup Instructions

### Prerequisites
- Python 3.9 or higher
- Google Places API key ([Get one here](https://developers.google.com/maps/documentation/places/web-service/get-api-key))

### Installation

1. **Clone or navigate to the project directory**
   ```bash
   cd TST_Tubes_Implementation
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv venv
   
   # On macOS/Linux:
   source venv/bin/activate
   
   # On Windows:
   venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   # Copy the example file
   cp .env.example .env
   
   # Edit .env and add your Google API key
   # GOOGLE_API_KEY=your_actual_api_key_here
   ```

### Running the Service

Start the FastAPI server:
```bash
uvicorn app.main:app --reload
```

The service will be available at:
- API: `http://localhost:8000`
- Interactive API docs: `http://localhost:8000/docs`
- ReDoc documentation: `http://localhost:8000/redoc`

## API Endpoints

### 1. Search Cafes

**Endpoint**: `GET /api/v1/search`

**Description**: Search for cafes within a specified radius of a location.

**Query Parameters**:
- `lat` (required): Latitude (-90 to 90)
- `lng` (required): Longitude (-180 to 180)
- `radius` (optional): Search radius in meters (default: 1000, max: 50000)

**Example Request**:
```bash
curl "http://localhost:8000/api/v1/search?lat=-6.9175&lng=107.6191&radius=1500"
```

**Example Response**:
```json
{
  "total": 3,
  "cafes": [
    {
      "id": "ChIJN1t_tDeuEmsRUsoyG83frY4",
      "name": "Kopi Kenangan",
      "address": "Jl. Braga No.10, Bandung",
      "latitude": -6.9175,
      "longitude": 107.6191,
      "rating": 4.5,
      "price_range": "MEDIUM",
      "distance_meters": 234.8
    },
    {
      "id": "ChIJAbC123XyZmsRTu8vG93ghL2",
      "name": "Starbucks",
      "address": "Jl. Dago No.25, Bandung",
      "latitude": -6.9185,
      "longitude": 107.6201,
      "rating": 4.3,
      "price_range": "HIGH",
      "distance_meters": 567.2
    }
  ]
}
```

### 2. Get Recommendations

**Endpoint**: `GET /api/v1/recommendations`

**Description**: Get filtered and ranked cafe recommendations based on preferences.

**Query Parameters**:
- `lat` (required): Latitude (-90 to 90)
- `lng` (required): Longitude (-180 to 180)
- `radius` (optional): Search radius in meters (default: 1000, max: 50000)
- `min_rating` (optional): Minimum rating filter (0-5, default: 0)
- `price_range` (optional): Comma-separated price ranges (e.g., "CHEAP,MEDIUM")
- `limit` (optional): Maximum results (1-100, default: 20)

**Valid Price Ranges**: `CHEAP`, `MEDIUM`, `HIGH`, `VERY_HIGH`, `LUXURY`, `UNKNOWN`

**Sorting Logic**:
1. Highest rating first
2. Nearest distance for cafes with the same rating

**Example Request 1**: Basic recommendations with minimum rating
```bash
curl "http://localhost:8000/api/v1/recommendations?lat=-6.9175&lng=107.6191&min_rating=4.2"
```

**Example Request 2**: Filter by price range
```bash
curl "http://localhost:8000/api/v1/recommendations?lat=-6.9175&lng=107.6191&min_rating=4.0&price_range=MEDIUM,HIGH&limit=10"
```

**Example Request 3**: Budget-friendly cafes
```bash
curl "http://localhost:8000/api/v1/recommendations?lat=-6.9175&lng=107.6191&price_range=CHEAP,MEDIUM&limit=5"
```

**Example Response**:
```json
{
  "total": 2,
  "cafes": [
    {
      "id": "ChIJN1t_tDeuEmsRUsoyG83frY4",
      "name": "Kopi Kenangan",
      "address": "Jl. Braga No.10, Bandung",
      "latitude": -6.9175,
      "longitude": 107.6191,
      "rating": 4.5,
      "price_range": "MEDIUM",
      "distance_meters": 234.8
    },
    {
      "id": "ChIJAbC123XyZmsRTu8vG93ghL2",
      "name": "Starbucks",
      "address": "Jl. Dago No.25, Bandung",
      "latitude": -6.9185,
      "longitude": 107.6201,
      "rating": 4.3,
      "price_range": "HIGH",
      "distance_meters": 567.2
    }
  ],
  "filters_applied": {
    "min_rating": 4.2,
    "price_ranges": ["MEDIUM", "HIGH"],
    "limit": 20
  }
}
```

### Additional Endpoints

**Health Check**: `GET /health`
```bash
curl http://localhost:8000/health
```

**Root Info**: `GET /`
```bash
curl http://localhost:8000/
```

## Testing with Popular Coordinates

### Bandung, Indonesia
```bash
curl "http://localhost:8000/api/v1/recommendations?lat=-6.9175&lng=107.6191&min_rating=4.0&limit=10"
```

### Jakarta, Indonesia
```bash
curl "http://localhost:8000/api/v1/recommendations?lat=-6.2088&lng=106.8456&min_rating=4.0&limit=10"
```

### Singapore
```bash
curl "http://localhost:8000/api/v1/recommendations?lat=1.3521&lng=103.8198&min_rating=4.0&limit=10"
```

## Error Handling

The API returns appropriate HTTP status codes:
- `200`: Successful request
- `400`: Invalid request parameters (e.g., invalid coordinates, price range)
- `500`: Internal server error or Google Places API error

**Example Error Response**:
```json
{
  "detail": "Failed to fetch cafes from Google Places API: API key invalid"
}
```

## Development

### Code Quality
- Strong typing throughout (Python type hints)
- Separation of concerns (domain, infrastructure, services, API)
- Proper error handling and logging
- Clean mapping between layers

### Adding New Features

**To add a new filter**:
1. Update `RecommendationService.filter_and_rank_cafes()` in `app/services/recommendation_service.py`
2. Add query parameter to `app/api/routers/recommendations.py`

**To add a new data source**:
1. Create a new client in `app/infrastructure/`
2. Update `SearchService` to use the new client

**To add a new endpoint**:
1. Create a new router in `app/api/routers/`
2. Include it in `app/main.py`

## Bounded Context Mapping

| Bounded Context | Code Location | Responsibilities |
|----------------|---------------|------------------|
| **BC1 (Catalog)** | `app/domain/models.py` | Domain entities, value objects, enums. Maps external API structures to internal models. |
| **BC2 (Search)** | `app/services/search_service.py` | Orchestrates search operations. Calls Google Places API, computes distances, returns domain entities. |
| **BC3 (Recommendation)** | `app/services/recommendation_service.py` | Applies business rules. Filters by rating/price, sorts results, applies limits. |

## Limitations & Notes

1. **No Persistence**: All data is fetched in real-time from Google Places API
2. **API Rate Limits**: Subject to Google Places API quotas and rate limits
3. **Data Freshness**: Data is as current as Google's index
4. **Distance Calculation**: Uses Haversine formula (great-circle distance), not driving distance
5. **Price Level Accuracy**: Depends on Google's price level data availability

## License

This project is for educational purposes.

## Support

For issues or questions, refer to:
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Google Places API Documentation](https://developers.google.com/maps/documentation/places/web-service)
