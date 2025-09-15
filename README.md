# Real Estate API

A comprehensive FastAPI-based REST API for managing real estate properties, users, and transactions with One ID (Yagona identifikatsiya tizimi) integration.

## 🚀 Features

- **Property Management**: Create, read, update, and delete real estate listings
- **User Authentication**: JWT-based authentication with role-based access control
- **One ID Integration**: Government Single Sign-On (SSO) authentication system
- **Search & Filtering**: Advanced search with multiple filters (price, location, area, etc.)
- **Image Management**: AWS S3 integration for property images
- **Category System**: Organized property categorization
- **Comment System**: User comments on properties
- **Location-based Search**: Find properties within specified radius
- **Admin Panel**: Administrative functions for system management

## 🏗️ Project Structure

```
real-estate-api/
├── app/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── endpoints/          # API endpoints
│   │   │   └── router.py          # Main router
│   │   └── deps.py                # Dependencies
│   ├── core/
│   │   ├── config.py              # Configuration settings
│   │   └── security.py            # Security utilities
│   ├── db/
│   │   ├── base.py                # Base model class
│   │   ├── init_db.py             # Database initialization
│   │   └── session.py             # Database session
│   ├── models/                    # SQLAlchemy models
│   ├── schemas/                   # Pydantic schemas
│   ├── services/                  # Business logic
│   └── utils/                     # Utility functions
├── alembic/                       # Database migrations
├── requirements.txt               # Python dependencies
├── docker-compose.yml            # Docker setup
└── README.md                     # This file
```

## 🛠️ Installation

### Prerequisites

- Python 3.8+
- PostgreSQL 12+
- Docker & Docker Compose (optional)

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd real-estate-api
   ```

2. **Create virtual environment**
   ```bash
   python -m venv env
   source env/bin/activate  # On Windows: env\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp example.env .env
   # Edit .env with your configuration
   ```

5. **Initialize database**
   ```bash
   python -m app.db.init_db
   ```

6. **Run the application**
   ```bash
   uvicorn app.main:app --reload
   ```

### Docker Setup

1. **Build and run with Docker Compose**
   ```bash
   docker-compose up --build
   ```

## ⚙️ Configuration

Create a `.env` file with the following variables:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/real_estate

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# AWS S3
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
AWS_REGION_NAME=us-east-1
AWS_S3_BUCKET_NAME=your-bucket-name

# CORS
BACKEND_CORS_ORIGINS=["http://localhost:3000", "http://localhost:8000"]
```

## 📚 API Documentation

Once the application is running, you can access:

- **Interactive API docs**: http://localhost:8000/docs
- **ReDoc documentation**: http://localhost:8000/redoc
- **Health check**: http://localhost:8000/health

## 🔐 Authentication

The API uses JWT tokens for authentication:

1. **Login**: `POST /api/v1/auth/login-admin`
2. **Include token**: Add `Authorization: Bearer <token>` header
3. **Refresh**: `POST /api/v1/auth/refresh`

## 🔐 One ID Integration

This API integrates with Uzbekistan's One ID (Yagona identifikatsiya tizimi) system for government Single Sign-On authentication.

### One ID Authentication Flow

1. **Frontend initiates OAuth2 flow** with One ID system
2. **User authenticates** through One ID portal
3. **One ID redirects** to our callback endpoint with authorization code
4. **Backend exchanges code** for access token
5. **User information** is retrieved and stored locally

### One ID Endpoints

#### Authentication Callback
```bash
POST /api/v1/one_id/auth/callback
{
  "code": "authorization_code_from_one_id",
  "state": "state_parameter"
}
```

Response:
```json
{
  "user": {
    "valid": true,
    "pin": "12345678901234",
    "user_id": "user123",
    "full_name": "John Doe",
    "first_name": "John",
    "last_name": "Doe",
    "middle_name": "Father",
    "passport_number": "AA1234567",
    "birth_date": "1990-01-01",
    "user_type": "I",
    "is_verified": true,
    "auth_method": "PKCSMETHOD"
  },
  "access_token": "one_id_access_token",
  "refresh_token": "one_id_refresh_token",
  "expires_in": 3600
}
```

#### Get User by PIN
```bash
GET /api/v1/one_id/user/{pin}
```

#### Get User by One ID User ID
```bash
GET /api/v1/one_id/user/one_id/{one_id_user_id}
```

#### Logout from One ID
```bash
POST /api/v1/one_id/logout
{
  "access_token": "one_id_access_token"
}
```

### One ID Configuration

Add the following environment variables:

```env
# One ID (Yagona identifikatsiya tizimi) Settings
ONE_ID_CLIENT_ID=your-one-id-client-id
ONE_ID_CLIENT_SECRET=your-one-id-client-secret
ONE_ID_REDIRECT_URI=https://qavat.uz/one_id/auth/callback
ONE_ID_SCOPE=myportal
ONE_ID_BASE_URL=https://sso.egov.uz/sso/oauth
```

### One ID Data Model

The system stores One ID information in a separate `OneIDInfo` table with One-to-One relationship to User:

- **Personal Information**: PIN, full name, passport number, birth date
- **Authentication Data**: One ID user ID, session ID, verification status
- **Legal Entity Data**: TIN for legal entities, authentication methods

## 🏠 Property Management

### Create Property
```bash
POST /api/v1/ads/
Authorization: Bearer <token>
{
  "title": "Beautiful 3-bedroom apartment",
  "description": "Modern apartment in city center",
  "price": 250000,
  "deal_type": "sale",
  "category_id": 1,
  "latitude": 41.33575242335,
  "longitude": 69.21214325235,
  "full_name": "John Doe",
  "email": "john@example.com",
  "phone_number": "+1234567890"
}
```

### Search Properties
```bash
GET /api/v1/ads/?q=apartment&min_price=200000&max_price=300000&city=Tashkent
```

### Location-based Search
```bash
GET /api/v1/ads/nearby?latitude=41.33575242335&longitude=69.21214325235&radius_km=5
```

## 🧪 Testing

Run tests with pytest:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/unit/test_services.py

# Run with verbose output
pytest -v
```

### Test Structure
```
tests/
├── unit/              # Unit tests
│   ├── test_services.py
│   ├── test_models.py
│   └── test_schemas.py
├── integration/       # Integration tests
│   ├── test_api.py
│   └── test_database.py
└── conftest.py       # Test configuration
```

## 📝 Database Migrations

Using Alembic for database migrations:

```bash
# Create a new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## 🚀 Deployment

### Production Considerations

1. **Environment Variables**: Use proper production values
2. **Database**: Use production PostgreSQL instance
3. **Security**: Change default admin credentials
4. **HTTPS**: Enable SSL/TLS
5. **Monitoring**: Add logging and monitoring
6. **Rate Limiting**: Implement API rate limiting

### Docker Production

```bash
docker build -t real-estate-api .
docker run -p 8000:8000 --env-file .env real-estate-api
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:

- Create an issue in the repository
- Contact the development team
- Check the API documentation

## 🔄 Changelog

### v1.1.0
- Added One ID (Yagona identifikatsiya tizimi) integration
- Implemented OAuth2 authentication flow with government SSO
- Created separate OneIDInfo model for One ID data
- Added One-to-One relationship between User and OneIDInfo
- Implemented user management with One ID information
- Added comprehensive One ID API endpoints

### v1.0.0
- Initial release
- Basic CRUD operations for properties
- User authentication system
- Image upload functionality
- Search and filtering capabilities
