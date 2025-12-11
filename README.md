# Cafe Recommendation Service

![CI/CD Pipeline](https://github.com/harfhanridzky/cafe-recommendation-service/actions/workflows/ci.yml/badge.svg)
![Python Version](https://img.shields.io/badge/python-3.10-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688)
![License](https://img.shields.io/badge/license-MIT-blue)

A FastAPI-based microservice for discovering and getting personalized cafe recommendations using Google Places API with JWT authentication.

## 🚀 Quick Start

```bash
# Clone and setup
git clone https://github.com/harfhanridzky/cafe-recommendation-service.git
cd cafe-recommendation-service
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY and JWT_SECRET_KEY

# Run server
uvicorn app.main:app --reload
# Visit: http://localhost:8000/docs
```

## 📁 Project Structure

```
cafe-recommendation-service/
├── app/
│   ├── api/routers/           # API endpoints
│   │   ├── auth.py            # Authentication
│   │   ├── search.py          # Public search
│   │   └── recommendations.py # Protected recommendations
│   ├── domain/models.py       # Domain entities (DDD)
│   ├── services/              # Business logic
│   │   ├── auth_service.py    # JWT & passwords
│   │   ├── user_service.py    # User management
│   │   ├── search_service.py  # Search orchestration
│   │   └── recommendation_service.py  # Filtering & ranking
│   ├── infrastructure/        # External integrations
│   ├── schemas/               # Pydantic models
│   ├── config.py             # Configuration
│   └── main.py               # FastAPI app
├── tests/                     # Test suite (TDD)
├── .github/workflows/ci.yml   # CI/CD pipeline
├── requirements.txt
└── setup.cfg                  # Test configuration
```

## 🏗️ Architecture (Domain-Driven Design)

**BC1 - Catalog (Domain Layer)**
- Maps Google Places API to internal domain entities
- Entities: `Cafe`, `Location`, `Rating`, `PriceRange`, `User`

**BC2 - Search Service**
- Orchestrates Google Places API calls
- Calculates distances using Haversine formula
- Maps external data to domain models

**BC3 - Recommendation Service**
- Filters by rating and price range
- Sorts by rating (descending) and distance (ascending)
- Applies result limits

## 🔑 Environment Variables

```env
# Required
GOOGLE_API_KEY=your_google_places_api_key
JWT_SECRET_KEY=your_secure_32_char_minimum_secret

# Optional (defaults shown)
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

Get Google API Key: https://developers.google.com/maps/documentation/places/web-service/get-api-key

## 📡 API Endpoints

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/v1/auth/register` | POST | ❌ | Register new user |
| `/api/v1/auth/login` | POST | ❌ | Login & get JWT token |
| `/api/v1/auth/me` | GET | ✅ | Get current user info |
| `/api/v1/search` | GET | ❌ | Search cafes (public) |
| `/api/v1/recommendations` | GET | ✅ | Get filtered recommendations |
| `/health` | GET | ❌ | Health check |
| `/` | GET | ❌ | API info |

## 🔐 Authentication Example

```bash
# 1. Register
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "securepass123"}'

# 2. Login (get JWT token)
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "securepass123"}'
# Response: {"access_token": "eyJ...", "token_type": "bearer", "expires_in": 1800}

# 3. Use token for protected endpoints
curl "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer eyJ..."
```

## 🔍 Search & Recommendations

### Public Search (No Auth Required)

```bash
# Basic search
curl "http://localhost:8000/api/v1/search?latitude=-6.2088&longitude=106.8456&radius=1000"

# Parameters:
# - latitude (required): -90 to 90
# - longitude (required): -180 to 180
# - radius (optional): meters, default 1500
```

### Recommendations (Auth Required)

```bash
# Get JWT token first
TOKEN=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "securepass123"}' | jq -r '.access_token')

# Get recommendations with filters
curl "http://localhost:8000/api/v1/recommendations?latitude=-6.2088&longitude=106.8456&min_rating=4.0&sort_by=rating&limit=10" \
  -H "Authorization: Bearer $TOKEN"

# Parameters:
# - latitude, longitude, radius (same as search)
# - min_rating (optional): 0.0 to 5.0
# - price_range (optional): cheap, moderate, expensive, very_expensive
# - sort_by (optional): rating, distance, price
# - limit (optional): max results, default 20
```

### Response Example

```json
{
  "cafes": [
    {
      "place_id": "ChIJ...",
      "name": "Kopi Kenangan",
      "location": {
        "latitude": -6.2088,
        "longitude": 106.8456
      },
      "rating": {
        "value": 4.5
      },
      "price_range": "moderate",
      "user_ratings_total": 250,
      "vicinity": "Jl. Sudirman No.123",
      "distance_km": 0.5
    }
  ]
}
```

## 🧪 Testing

This project follows **Test-Driven Development (TDD)** with comprehensive test coverage.

### Run Tests

```bash
# All tests
pytest

# With coverage report
pytest --cov=app --cov-report=term-missing

# Specific test file
pytest tests/test_auth_service.py -v

# HTML coverage report
pytest --cov=app --cov-report=html
open htmlcov/index.html
```

### Test Suite

```
tests/
├── test_domain_models.py      # Domain entities & value objects
├── test_auth_service.py       # JWT & password hashing
├── test_user_service.py       # User management
├── test_search_service.py     # Search orchestration
├── test_recommendation_service.py  # Filtering & sorting
├── test_api_auth.py           # Auth endpoints
├── test_api_search.py         # Search endpoint
├── test_api_recommendations.py  # Recommendations endpoint
├── test_integration.py        # End-to-end flows
└── test_security.py           # Security tests
```

### CI/CD Pipeline

GitHub Actions automatically runs on every push:
- ✅ Code linting (flake8)
- ✅ Code formatting (black)
- ✅ Import sorting (isort)
- ✅ Type checking (mypy)
- ✅ Unit & integration tests
- ✅ Test coverage reporting

View workflow: `.github/workflows/ci.yml`

## 🛡️ Security Features

- **Password Security**: bcrypt hashing with salt
- **JWT Authentication**: HS256 algorithm, 30-minute expiry
- **Input Validation**: Pydantic models with strict validation
- **No Secrets in Code**: Environment variables for sensitive data
- **SQL Injection Prevention**: No database (API-only architecture)
- **CORS Configuration**: Configurable allowed origins

## 📊 Domain Model

### Entities & Value Objects

```python
# Entity: Cafe
Cafe {
    place_id: str
    name: str
    location: Location
    rating: Rating
    price_range: PriceRange
    user_ratings_total: int
    vicinity: str
    distance_km: float
}

# Value Object: Location
Location {
    latitude: float   # -90 to 90
    longitude: float  # -180 to 180
}

# Value Object: Rating
Rating {
    value: float  # 0.0 to 5.0
}

# Enum: PriceRange
PriceRange = "cheap" | "moderate" | "expensive" | "very_expensive"
```

## 🚦 Error Handling

| Status Code | Description |
|-------------|-------------|
| 200 | Success |
| 400 | Bad request (invalid parameters) |
| 401 | Unauthorized (invalid/expired token) |
| 403 | Forbidden (no token provided) |
| 404 | Not found |
| 422 | Validation error |
| 500 | Internal server error |

## 🔧 Development

### Code Quality

```bash
# Format code
black app/

# Sort imports
isort app/

# Lint code
flake8 app/

# Type checking
mypy app/ --ignore-missing-imports
```

### Project Dependencies

```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-dotenv==1.0.0
httpx==0.25.2
```

## 📝 API Documentation

Interactive API documentation available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🌍 Popular Test Coordinates

```bash
# Jakarta, Indonesia
latitude=-6.2088&longitude=106.8456

# Bandung, Indonesia
latitude=-6.9175&longitude=107.6191

# Singapore
latitude=1.3521&longitude=103.8198

# Bangkok, Thailand
latitude=13.7563&longitude=100.5018
```

## ⚠️ Limitations

- No persistence layer (all data fetched on-demand)
- Subject to Google Places API quotas and rate limits
- Distance calculation uses great-circle formula (not driving distance)
- Price level data depends on Google's availability

## 📄 License

This project is for educational purposes.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📞 Support

- **Repository**: https://github.com/harfhanridzky/cafe-recommendation-service
- **Issues**: https://github.com/harfhanridzky/cafe-recommendation-service/issues
- **API Docs**: [FastAPI Documentation](https://fastapi.tiangolo.com/)
- **Google Places API**: [Documentation](https://developers.google.com/maps/documentation/places/web-service)

---

**Built with**: FastAPI • Python • Google Places API • JWT • TDD • CI/CD
