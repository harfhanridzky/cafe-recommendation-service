# Cafe Recommendation Service - Architecture Diagram

## System Flow Diagram

```
┌─────────────┐
│   Client    │
│  (Browser/  │
│    cURL)    │
└──────┬──────┘
       │
       │ HTTP Request
       ▼
┌─────────────────────────────────────────────────────────────────┐
│                         FastAPI Application                      │
│                            (main.py)                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    API Layer (Routers)                     │  │
│  ├──────────────────────────────────────────────────────────┤  │
│  │  /api/v1/search          │  /api/v1/recommendations       │  │
│  │  (search.py)             │  (recommendations.py)          │  │
│  └────────┬─────────────────┴──────────────┬─────────────────┘  │
│           │                                 │                    │
│           │                                 │                    │
│  ┌────────▼─────────────────────────────────▼─────────────────┐ │
│  │              Service Layer (Business Logic)                 │ │
│  ├─────────────────────────────────────────────────────────────┤ │
│  │  BC2: SearchService         │  BC3: RecommendationService  │ │
│  │  - search_cafes()            │  - filter_and_rank_cafes()   │ │
│  │  - calculate_distance()      │  - Filter by rating          │ │
│  │  - Map Google → Domain       │  - Filter by price           │ │
│  │                              │  - Sort & limit              │ │
│  └────────┬─────────────────────┴──────────────────────────────┘ │
│           │                                                        │
│           │                                                        │
│  ┌────────▼────────────────────────────────────────────────────┐ │
│  │          Infrastructure Layer (External APIs)               │ │
│  ├─────────────────────────────────────────────────────────────┤ │
│  │              GooglePlacesClient                             │ │
│  │  - search_nearby_cafes()                                    │ │
│  │  - get_place_details()                                      │ │
│  └────────┬────────────────────────────────────────────────────┘ │
│           │                                                        │
└───────────┼────────────────────────────────────────────────────────┘
            │
            │ HTTPS Request
            ▼
   ┌────────────────────┐
   │  Google Places API │
   │  (External Service) │
   └────────────────────┘


┌─────────────────────────────────────────────────────────────────┐
│                 Domain Layer (BC1: Catalog)                      │
│                       (models.py)                                │
├─────────────────────────────────────────────────────────────────┤
│  Cafe (Entity)                                                   │
│  ├── id: str                                                     │
│  ├── name: str                                                   │
│  ├── address: str                                                │
│  ├── location: Location                                          │
│  ├── rating: Rating                                              │
│  ├── price_range: PriceRange                                     │
│  └── distance_meters: float                                      │
│                                                                   │
│  Location (Value Object)    Rating (Value Object)                │
│  ├── latitude: float         ├── value: float (0.0-5.0)         │
│  └── longitude: float        └── comparison operators           │
│                                                                   │
│  PriceRange (Enum)                                               │
│  ├── CHEAP (0)                                                   │
│  ├── MEDIUM (1)                                                  │
│  ├── HIGH (2)                                                    │
│  ├── VERY_HIGH (3)                                               │
│  ├── LUXURY (4)                                                  │
│  └── UNKNOWN (None)                                              │
└─────────────────────────────────────────────────────────────────┘
```

## Request Flow: Search

```
1. Client Request
   GET /api/v1/search?lat=-6.9175&lng=107.6191&radius=1500
   
2. API Router (search.py)
   ├── Validate query parameters
   └── Call SearchService
   
3. SearchService (BC2)
   ├── Call GooglePlacesClient.search_nearby_cafes()
   ├── Receive raw Google Places data
   ├── For each result:
   │   ├── Extract coordinates, rating, price_level
   │   ├── Calculate distance (Haversine)
   │   └── Map to Cafe entity (BC1)
   └── Return List[Cafe]
   
4. GooglePlacesClient
   ├── Build API request URL
   ├── Add API key and parameters
   ├── Send HTTPS request to Google
   ├── Handle errors (network, API status)
   └── Return raw JSON results
   
5. API Router
   ├── Map List[Cafe] → List[CafeResponse]
   └── Return SearchResponse
   
6. Client receives JSON response
```

## Request Flow: Recommendations

```
1. Client Request
   GET /api/v1/recommendations?lat=-6.9175&lng=107.6191
       &min_rating=4.0&price_range=MEDIUM,HIGH&limit=10
   
2. API Router (recommendations.py)
   ├── Validate query parameters
   ├── Parse price_range string → List[PriceRange]
   └── Orchestrate services
   
3. SearchService (BC2)
   ├── Fetch all cafes near location
   └── Return List[Cafe]
   
4. RecommendationService (BC3)
   ├── Filter by min_rating (4.0)
   │   └── Keep only cafes with rating >= 4.0
   ├── Filter by price_range (MEDIUM, HIGH)
   │   └── Keep only cafes with matching price
   ├── Sort results:
   │   ├── Primary: rating (descending)
   │   └── Secondary: distance (ascending)
   └── Apply limit (10)
   
5. API Router
   ├── Map List[Cafe] → List[CafeResponse]
   ├── Add filters_applied metadata
   └── Return RecommendationResponse
   
6. Client receives filtered & sorted JSON
```

## Bounded Contexts Detail

```
┌─────────────────────────────────────────────────────────────────┐
│ BC1: CATALOG (Domain)                                           │
├─────────────────────────────────────────────────────────────────┤
│ Purpose: Define domain entities and business rules              │
│                                                                  │
│ Responsibilities:                                                │
│ • Define Cafe entity structure                                  │
│ • Define value objects (Location, Rating)                       │
│ • Define business enums (PriceRange)                            │
│ • Validate domain rules                                         │
│ • Provide mapping from Google price_level                       │
│                                                                  │
│ Files: app/domain/models.py                                     │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ BC2: SEARCH (Service)                                           │
├─────────────────────────────────────────────────────────────────┤
│ Purpose: Orchestrate cafe search operations                     │
│                                                                  │
│ Responsibilities:                                                │
│ • Call Google Places API via client                             │
│ • Calculate distance from user location                         │
│ • Map external API structure to domain entities                 │
│ • Handle API errors gracefully                                  │
│ • Return domain-compliant cafe list                             │
│                                                                  │
│ Files: app/services/search_service.py                           │
│        app/infrastructure/google_places_client.py               │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ BC3: RECOMMENDATION (Service)                                   │
├─────────────────────────────────────────────────────────────────┤
│ Purpose: Apply recommendation business logic                    │
│                                                                  │
│ Responsibilities:                                                │
│ • Filter cafes by minimum rating                                │
│ • Filter cafes by price range preferences                       │
│ • Sort by rating (high to low)                                  │
│ • Sort by distance (near to far) for same rating               │
│ • Apply result limits                                           │
│ • Return curated recommendation list                            │
│                                                                  │
│ Files: app/services/recommendation_service.py                   │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow & Transformation

```
Google Places API Response
          ↓
    {
      "place_id": "ChIJ...",
      "name": "Kopi Kenangan",
      "vicinity": "Jl. Braga No.10",
      "geometry": {
        "location": {"lat": -6.9175, "lng": 107.6191}
      },
      "rating": 4.5,
      "price_level": 1
    }
          ↓
    [GooglePlacesClient returns raw dict]
          ↓
    [SearchService maps to Domain]
          ↓
    Cafe(
      id="ChIJ...",
      name="Kopi Kenangan",
      address="Jl. Braga No.10",
      location=Location(-6.9175, 107.6191),
      rating=Rating(4.5),
      price_range=PriceRange.MEDIUM,  ← Mapped from price_level=1
      distance_meters=234.8  ← Calculated via Haversine
    )
          ↓
    [RecommendationService filters & sorts]
          ↓
    [API Router maps to Response schema]
          ↓
    CafeResponse {
      "id": "ChIJ...",
      "name": "Kopi Kenangan",
      "address": "Jl. Braga No.10",
      "latitude": -6.9175,
      "longitude": 107.6191,
      "rating": 4.5,
      "price_range": "MEDIUM",
      "distance_meters": 234.8
    }
          ↓
    [JSON serialization]
          ↓
    Client receives JSON
```

## Layer Dependencies

```
┌─────────────┐
│  API Layer  │  (FastAPI routers)
└──────┬──────┘
       │ depends on
       ▼
┌─────────────┐
│   Service   │  (Business logic)
│    Layer    │
└──────┬──────┘
       │ depends on
       ├─────────────────┐
       ▼                 ▼
┌──────────────┐  ┌──────────────┐
│ Domain Layer │  │Infrastructure│
│ (BC1 Models) │  │    Layer     │
└──────────────┘  └──────────────┘
                         │
                         ▼
                  ┌──────────────┐
                  │ Google Places│
                  │     API      │
                  └──────────────┘
```

## Technology Stack

```
┌─────────────────────────────────────────────────────────────┐
│ Framework: FastAPI 0.104.1                                  │
│ Server: Uvicorn 0.24.0                                      │
│ Validation: Pydantic 2.5.0                                  │
│ HTTP Client: httpx 0.25.2                                   │
│ Config: pydantic-settings 2.1.0                             │
│ Environment: python-dotenv 1.0.0                            │
└─────────────────────────────────────────────────────────────┘
```

## Error Handling Flow

```
Exception in any layer
        ↓
    Caught by API Router
        ↓
    Mapped to HTTP status
        ├─── 400: Validation errors
        ├─── 500: API errors
        └─── 500: Unexpected errors
        ↓
    ErrorResponse returned
        ↓
    Client receives JSON error
```

## Key Design Principles

1. **Separation of Concerns**: Each layer has clear responsibilities
2. **Domain-Driven Design**: Business logic in domain entities
3. **Dependency Inversion**: Services depend on abstractions
4. **Type Safety**: Full type hints throughout
5. **No Persistence**: Stateless, real-time data
6. **Error Isolation**: Errors handled at appropriate layers
7. **Clean Mapping**: Clear transformation between layers

---

This architecture ensures:
- ✅ Maintainability through clear separation
- ✅ Testability through dependency injection
- ✅ Scalability through stateless design
- ✅ Reliability through proper error handling
- ✅ Type safety through strong typing
