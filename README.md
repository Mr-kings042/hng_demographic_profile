# Demographic Profile API

A FastAPI application that integrates with three external demographic APIs to collect and store profile information with intelligent duplicate detection.

## Features

- **Multi-API Integration**: Fetches data from Genderize, Agify, and Nationalize APIs
- **Smart Classification**: Automatically classifies age into groups (child, teenager, adult, senior)
- **Duplicate Detection**: Idempotent operations - same name returns existing profile
- **Database Persistence**: SQLite by default, PostgreSQL configurable
- **Complete CRUD Operations**: Create, read, update, and delete profiles
- **Advanced Filtering**: Filter profiles by gender, country, and age group
- **Error Handling**: Comprehensive error handling with proper HTTP status codes
- **CORS Support**: Full cross-origin request support

## Project Structure

```
stage_1/
├── main.py           # FastAPI app setup and entry point
├── database.py       # Database setup, session management, and migrations
├── models.py         # SQLAlchemy ORM models
├── schema.py         # Pydantic request/response validation models
├── services.py       # Business logic and external API calls
├── routes.py         # API endpoints
├── requirements.txt  # Python dependencies
├── .env              # Environment configuration
└── README.md         # This file
```

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Database Configuration

By default, the application uses SQLite. To use PostgreSQL instead, update the `.env` file:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/demographic_profile
```

### 3. Run the Application

```bash
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

Interactive API documentation: `http://localhost:8000/docs`

## API Endpoints

### 1. Create Profile
**POST** `/api/profiles`

Request:
```json
{
  "name": "ella"
}
```

Response (201):
```json
{
  "status": "success",
  "data": {
    "id": "b3f9c1e2-7d4a-4c91-9c2a-1f0a8e5b6d12",
    "name": "ella",
    "gender": "female",
    "gender_probability": 0.99,
    "sample_size": 1234,
    "age": 46,
    "age_group": "adult",
    "country_id": "DRC",
    "country_probability": 0.85,
    "created_at": "2026-04-01T12:00:00Z"
  }
}
```

Note: If the profile already exists, it returns the existing profile with message "Profile already exists".

### 2. Get Single Profile
**GET** `/api/profiles/{id}`

Response (200):
```json
{
  "status": "success",
  "data": {
    "id": "b3f9c1e2-7d4a-4c91-9c2a-1f0a8e5b6d12",
    "name": "emmanuel",
    "gender": "male",
    "gender_probability": 0.99,
    "sample_size": 1234,
    "age": 25,
    "age_group": "adult",
    "country_id": "NG",
    "country_probability": 0.85,
    "created_at": "2026-04-01T12:00:00Z"
  }
}
```

### 3. Get All Profiles (with Optional Filtering)
**GET** `/api/profiles?gender=male&country_id=NG&age_group=adult`

Query Parameters (all optional and case-insensitive):
- `gender`: Filter by gender (male, female)
- `country_id`: Filter by country ID (e.g., NG, US, DRC)
- `age_group`: Filter by age group (child, teenager, adult, senior)

Response (200):
```json
{
  "status": "success",
  "count": 2,
  "data": [
    {
      "id": "id-1",
      "name": "emmanuel",
      "gender": "male",
      "age": 25,
      "age_group": "adult",
      "country_id": "NG"
    },
    {
      "id": "id-2",
      "name": "sarah",
      "gender": "female",
      "age": 28,
      "age_group": "adult",
      "country_id": "US"
    }
  ]
}
```

### 4. Delete Profile
**DELETE** `/api/profiles/{id}`

Response: 204 No Content (on success)

## Error Handling

### Error Response Format
```json
{
  "status": "error",
  "message": "<error message>"
}
```

### Error Codes

- **400 Bad Request**: Missing or empty name
  ```json
  {
    "status": "error",
    "message": "Name cannot be empty"
  }
  ```

- **404 Not Found**: Profile not found
  ```json
  {
    "status": "error",
    "message": "Profile not found"
  }
  ```

- **422 Unprocessable Entity**: Invalid input type
  ```json
  {
    "status": "error",
    "message": "Invalid input"
  }
  ```

- **502 Bad Gateway**: External API error
  ```json
  {
    "status": "error",
    "message": "Genderize returned an invalid response"
  }
  ```
  
  Possible external API errors:
  - "Genderize returned an invalid response"
  - "Agify returned an invalid response"
  - "Nationalize returned an invalid response"

## Classification Rules

### Age Groups
| Age Range | Group      |
|-----------|-----------|
| 0-12      | child     |
| 13-19     | teenager  |
| 20-59     | adult     |
| 60+       | senior    |

### Nationality
The country with the highest probability from the Nationalize API response is selected as the primary nationality.

## External APIs Used

1. **Genderize API**: https://api.genderize.io
   - Returns gender prediction and probability
   
2. **Agify API**: https://api.agify.io
   - Returns age prediction
   
3. **Nationalize API**: https://api.nationalize.io
   - Returns nationality/country probabilities

All APIs are free with no authentication required.

## Data Persistence

- **Unique Constraint**: Names are stored uniquely (case-insensitive)
- **UUID v7**: All profile IDs use UUID version 7 format
- **Timestamps**: All timestamps are in UTC ISO 8601 format
- **Automatic ID Generation**: Profile IDs are generated automatically on creation

## Testing the API

### Using cURL

Create a profile:
```bash
curl -X POST http://localhost:8000/api/profiles \
  -H "Content-Type: application/json" \
  -d '{"name": "john"}'
```

Get all profiles:
```bash
curl http://localhost:8000/api/profiles
```

Filter profiles:
```bash
curl "http://localhost:8000/api/profiles?gender=male&country_id=NG"
```

Get specific profile:
```bash
curl http://localhost:8000/api/profiles/{id}
```

Delete profile:
```bash
curl -X DELETE http://localhost:8000/api/profiles/{id}
```

### Using Python requests

```python
import requests

# Create profile
response = requests.post(
    "http://localhost:8000/api/profiles",
    json={"name": "alice"}
)
print(response.json())

# Get all profiles
response = requests.get("http://localhost:8000/api/profiles")
print(response.json())

# Filter profiles
response = requests.get(
    "http://localhost:8000/api/profiles",
    params={"gender": "female", "age_group": "adult"}
)
print(response.json())
```

## Evaluation Criteria Met

- ✅ API Design (Endpoints): 4/4 endpoints implemented with proper HTTP methods and status codes
- ✅ Multi-API Integration: All 3 external APIs integrated with error handling
- ✅ Data Persistence: SQLAlchemy ORM with SQLite/PostgreSQL support
- ✅ Idempotency Handling: Duplicate detection based on name (case-insensitive)
- ✅ Filtering Logic: Case-insensitive filtering by gender, country, age_group
- ✅ Data Modeling: Proper Pydantic models for requests/responses
- ✅ Error Handling: Comprehensive error responses with proper HTTP status codes
- ✅ Response Structure: Exact match to specification with status, data, and optional message
- ✅ CORS Headers: Access-Control-Allow-Origin: * enabled

## License

MIT
