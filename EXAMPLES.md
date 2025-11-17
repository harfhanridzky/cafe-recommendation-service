# API Usage Examples

## Quick Reference

Base URL: `http://localhost:8000`  
API Version: `v1`  
Documentation: `http://localhost:8000/docs`

---

## Example 1: Basic Search

### Request
```bash
curl "http://localhost:8000/api/v1/search?lat=-6.9175&lng=107.6191&radius=1500"
```

### Response
```json
{
  "total": 15,
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
      "name": "Starbucks Dago",
      "address": "Jl. Dago No.25, Bandung",
      "latitude": -6.9185,
      "longitude": 107.6201,
      "rating": 4.3,
      "price_range": "HIGH",
      "distance_meters": 567.2
    },
    {
      "id": "ChIJXyZ789AbcDeFgHiJkLmNoPq",
      "name": "Warung Kopi Imah",
      "address": "Jl. Riau No.5, Bandung",
      "latitude": -6.9165,
      "longitude": 107.6185,
      "rating": 4.7,
      "price_range": "CHEAP",
      "distance_meters": 892.5
    }
  ]
}
```

**Use Case**: "Show me all cafes within 1.5km"

---

## Example 2: High-Rated Recommendations

### Request
```bash
curl "http://localhost:8000/api/v1/recommendations?lat=-6.9175&lng=107.6191&min_rating=4.2&limit=5"
```

### Response
```json
{
  "total": 5,
  "cafes": [
    {
      "id": "ChIJXyZ789AbcDeFgHiJkLmNoPq",
      "name": "Warung Kopi Imah",
      "address": "Jl. Riau No.5, Bandung",
      "latitude": -6.9165,
      "longitude": 107.6185,
      "rating": 4.7,
      "price_range": "CHEAP",
      "distance_meters": 892.5
    },
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
      "name": "Starbucks Dago",
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
    "price_ranges": null,
    "limit": 5
  }
}
```

**Use Case**: "I want the best cafes (rating ≥ 4.2), show top 5"

---

## Example 3: Budget-Friendly Cafes

### Request
```bash
curl "http://localhost:8000/api/v1/recommendations?lat=-6.9175&lng=107.6191&price_range=CHEAP,MEDIUM&limit=10"
```

### Response
```json
{
  "total": 8,
  "cafes": [
    {
      "id": "ChIJXyZ789AbcDeFgHiJkLmNoPq",
      "name": "Warung Kopi Imah",
      "address": "Jl. Riau No.5, Bandung",
      "latitude": -6.9165,
      "longitude": 107.6185,
      "rating": 4.7,
      "price_range": "CHEAP",
      "distance_meters": 892.5
    },
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
      "id": "ChIJqRsTuVwXyZAbCdEfGhIjKlM",
      "name": "Kedai Kopi Gayo",
      "address": "Jl. Merdeka No.15, Bandung",
      "latitude": -6.9169,
      "longitude": 107.6178,
      "rating": 4.4,
      "price_range": "CHEAP",
      "distance_meters": 1245.3
    }
  ],
  "filters_applied": {
    "min_rating": 0.0,
    "price_ranges": ["CHEAP", "MEDIUM"],
    "limit": 10
  }
}
```

**Use Case**: "Show affordable cafes only (cheap or medium price)"

---

## Example 4: Premium Cafes with High Rating

### Request
```bash
curl "http://localhost:8000/api/v1/recommendations?lat=-6.9175&lng=107.6191&min_rating=4.5&price_range=HIGH,VERY_HIGH,LUXURY"
```

### Response
```json
{
  "total": 2,
  "cafes": [
    {
      "id": "ChIJmNoPqRsTuVwXyZAbCdEfGh",
      "name": "Blue Terrace Coffee",
      "address": "Jl. Cihampelas No.100, Bandung",
      "latitude": -6.9155,
      "longitude": 107.6195,
      "rating": 4.8,
      "price_range": "HIGH",
      "distance_meters": 345.6
    },
    {
      "id": "ChIJhIjKlMnOpQrStUvWxYzAbC",
      "name": "The Rooftop Cafe & Lounge",
      "address": "Jl. Sudirman No.55, Bandung",
      "latitude": -6.9182,
      "longitude": 107.6203,
      "rating": 4.6,
      "price_range": "LUXURY",
      "distance_meters": 678.9
    }
  ],
  "filters_applied": {
    "min_rating": 4.5,
    "price_ranges": ["HIGH", "VERY_HIGH", "LUXURY"],
    "limit": 20
  }
}
```

**Use Case**: "Find premium cafes with excellent ratings"

---

## Example 5: Nearest Cafes (Any Rating)

### Request
```bash
curl "http://localhost:8000/api/v1/search?lat=-6.9175&lng=107.6191&radius=500"
```

### Response
```json
{
  "total": 4,
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
      "id": "ChIJmNoPqRsTuVwXyZAbCdEfGh",
      "name": "Blue Terrace Coffee",
      "address": "Jl. Cihampelas No.100, Bandung",
      "latitude": -6.9155,
      "longitude": 107.6195,
      "rating": 4.8,
      "price_range": "HIGH",
      "distance_meters": 345.6
    },
    {
      "id": "ChIJcDeFgHiJkLmNoPqRsTuVwX",
      "name": "Cafe Latte Art",
      "address": "Jl. Asia Afrika No.8, Bandung",
      "latitude": -6.9178,
      "longitude": 107.6188,
      "rating": 4.1,
      "price_range": "MEDIUM",
      "distance_meters": 456.2
    }
  ]
}
```

**Use Case**: "What cafes are within 500m walking distance?"

---

## Example 6: Jakarta Search

### Request
```bash
curl "http://localhost:8000/api/v1/recommendations?lat=-6.2088&lng=106.8456&min_rating=4.0&limit=5"
```

**Use Case**: Different location (Jakarta instead of Bandung)

---

## Example 7: Error - Invalid Coordinates

### Request
```bash
curl "http://localhost:8000/api/v1/search?lat=95&lng=107.6191"
```

### Response (400 Bad Request)
```json
{
  "detail": [
    {
      "type": "less_than_equal",
      "loc": ["query", "lat"],
      "msg": "Input should be less than or equal to 90",
      "input": "95",
      "ctx": {"le": 90.0}
    }
  ]
}
```

---

## Example 8: Error - Invalid Price Range

### Request
```bash
curl "http://localhost:8000/api/v1/recommendations?lat=-6.9175&lng=107.6191&price_range=EXPENSIVE"
```

### Response (400 Bad Request)
```json
{
  "detail": "Invalid price range. Valid values: CHEAP, MEDIUM, HIGH, VERY_HIGH, LUXURY, UNKNOWN"
}
```

---

## Example 9: Health Check

### Request
```bash
curl "http://localhost:8000/health"
```

### Response
```json
{
  "status": "healthy",
  "service": "Cafe Recommendation Service"
}
```

---

## Example 10: Root Endpoint

### Request
```bash
curl "http://localhost:8000/"
```

### Response
```json
{
  "name": "Cafe Recommendation Service",
  "version": "1.0.0",
  "description": "Cafe Recommendation Service API",
  "endpoints": {
    "docs": "/docs",
    "search": "/api/v1/search",
    "recommendations": "/api/v1/recommendations"
  }
}
```

---

## Common Use Cases

### Use Case 1: "Find cafes near me"
```bash
curl "http://localhost:8000/api/v1/search?lat=YOUR_LAT&lng=YOUR_LNG&radius=1000"
```

### Use Case 2: "Recommend best cafes"
```bash
curl "http://localhost:8000/api/v1/recommendations?lat=YOUR_LAT&lng=YOUR_LNG&min_rating=4.0"
```

### Use Case 3: "Affordable cafes only"
```bash
curl "http://localhost:8000/api/v1/recommendations?lat=YOUR_LAT&lng=YOUR_LNG&price_range=CHEAP,MEDIUM"
```

### Use Case 4: "Top 3 nearest premium cafes"
```bash
curl "http://localhost:8000/api/v1/recommendations?lat=YOUR_LAT&lng=YOUR_LNG&min_rating=4.5&price_range=HIGH,LUXURY&limit=3"
```

### Use Case 5: "Student budget (cheap, decent rating)"
```bash
curl "http://localhost:8000/api/v1/recommendations?lat=YOUR_LAT&lng=YOUR_LNG&min_rating=4.0&price_range=CHEAP"
```

---

## Query Parameter Reference

### `/api/v1/search`

| Parameter | Type    | Required | Default | Range/Values | Description |
|-----------|---------|----------|---------|--------------|-------------|
| `lat`     | float   | Yes      | -       | -90 to 90    | Latitude |
| `lng`     | float   | Yes      | -       | -180 to 180  | Longitude |
| `radius`  | integer | No       | 1000    | 1 to 50000   | Search radius (meters) |

### `/api/v1/recommendations`

| Parameter     | Type    | Required | Default | Range/Values | Description |
|---------------|---------|----------|---------|--------------|-------------|
| `lat`         | float   | Yes      | -       | -90 to 90    | Latitude |
| `lng`         | float   | Yes      | -       | -180 to 180  | Longitude |
| `radius`      | integer | No       | 1000    | 1 to 50000   | Search radius (meters) |
| `min_rating`  | float   | No       | 0.0     | 0 to 5       | Minimum rating filter |
| `price_range` | string  | No       | null    | See below    | Comma-separated price ranges |
| `limit`       | integer | No       | 20      | 1 to 100     | Maximum results |

**Valid price_range values**: `CHEAP`, `MEDIUM`, `HIGH`, `VERY_HIGH`, `LUXURY`, `UNKNOWN`

---

## Testing with curl

### Simple Test
```bash
# Test if server is running
curl http://localhost:8000/health

# Basic search
curl "http://localhost:8000/api/v1/search?lat=-6.9175&lng=107.6191"
```

### Pretty Print with jq
```bash
curl -s "http://localhost:8000/api/v1/search?lat=-6.9175&lng=107.6191" | jq
```

### Save Response to File
```bash
curl "http://localhost:8000/api/v1/recommendations?lat=-6.9175&lng=107.6191&min_rating=4.0" \
  -o response.json
```

### Check Response Time
```bash
curl -w "\nTime: %{time_total}s\n" \
  "http://localhost:8000/api/v1/search?lat=-6.9175&lng=107.6191"
```

---

## Using the Provided Test Script

Run all tests automatically:
```bash
./test_api.sh
```

Make sure the server is running before executing tests!

---

## Interactive API Documentation

Visit `http://localhost:8000/docs` for:
- Interactive API playground
- Try endpoints directly from browser
- Automatic request/response examples
- Schema validation
- Download OpenAPI spec

---

## Response Fields Explained

### CafeResponse Fields

- **id**: Google Place ID (unique identifier)
- **name**: Cafe name from Google Places
- **address**: Street address or vicinity
- **latitude**: Cafe location latitude
- **longitude**: Cafe location longitude
- **rating**: Google rating (0.0 to 5.0)
- **price_range**: Price category (CHEAP to LUXURY)
- **distance_meters**: Distance from search center

### Sorting Logic

Recommendations are sorted by:
1. **Rating** (highest first) - Priority 1
2. **Distance** (nearest first) - Priority 2 (tie-breaker)

Example: A 4.7-rated cafe 500m away appears before a 4.5-rated cafe 200m away.

---

**Note**: All examples assume the server is running on `localhost:8000`. Adjust the base URL if deployed elsewhere.
