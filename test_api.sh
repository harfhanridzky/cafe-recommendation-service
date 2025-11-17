#!/bin/bash

# Test script for Cafe Recommendation Service
# Make sure the server is running on localhost:8000

BASE_URL="http://localhost:8000"

echo "🧪 Testing Cafe Recommendation Service"
echo "========================================"
echo ""

# Test 1: Health check
echo "Test 1: Health Check"
echo "GET $BASE_URL/health"
curl -s "$BASE_URL/health" | python3 -m json.tool
echo -e "\n"

# Test 2: Root endpoint
echo "Test 2: Root Endpoint"
echo "GET $BASE_URL/"
curl -s "$BASE_URL/" | python3 -m json.tool
echo -e "\n"

# Test 3: Search cafes in Bandung
echo "Test 3: Search Cafes (Bandung, Indonesia)"
echo "GET $BASE_URL/api/v1/search?lat=-6.9175&lng=107.6191&radius=1500"
curl -s "$BASE_URL/api/v1/search?lat=-6.9175&lng=107.6191&radius=1500" | python3 -m json.tool
echo -e "\n"

# Test 4: Get recommendations with minimum rating
echo "Test 4: Get Recommendations (min rating 4.0)"
echo "GET $BASE_URL/api/v1/recommendations?lat=-6.9175&lng=107.6191&min_rating=4.0&limit=10"
curl -s "$BASE_URL/api/v1/recommendations?lat=-6.9175&lng=107.6191&min_rating=4.0&limit=10" | python3 -m json.tool
echo -e "\n"

# Test 5: Get recommendations with price filter
echo "Test 5: Get Recommendations (price filter: CHEAP,MEDIUM)"
echo "GET $BASE_URL/api/v1/recommendations?lat=-6.9175&lng=107.6191&price_range=CHEAP,MEDIUM&limit=5"
curl -s "$BASE_URL/api/v1/recommendations?lat=-6.9175&lng=107.6191&price_range=CHEAP,MEDIUM&limit=5" | python3 -m json.tool
echo -e "\n"

echo "✅ All tests completed!"
echo ""
echo "For more detailed testing, visit: $BASE_URL/docs"
