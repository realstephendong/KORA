# Travel Planner Backend

A Flask-based backend API for an agentic travel planner application with Auth0 authentication.

## Features

- **Flask Application Factory Pattern**: Modular and scalable application structure
- **Auth0 Authentication**: JWT-based authentication for protected endpoints
- **PostgreSQL Database**: SQLAlchemy ORM with PostgreSQL support
- **CORS Support**: Cross-origin resource sharing for frontend integration
- **Environment Configuration**: Secure configuration management with .env files

## Project Structure

```
backend/
├── app/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── auth.py          # Auth0 authentication decorators
│   │   └── routes.py        # API endpoints
│   ├── models/
│   │   ├── __init__.py
│   │   └── user.py          # User model
│   └── __init__.py          # Application factory
├── config.py                # Configuration settings
├── run.py                   # Application entry point
├── requirements.txt         # Python dependencies
├── env.example             # Environment variables template
└── README.md               # This file
```

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Environment Configuration

Copy the example environment file and configure your settings:

```bash
cp env.example .env
```

Edit the `.env` file with your actual values:

```env
# Flask Configuration
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your_very_secret_key_here

# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/travel_planner

# Auth0 Configuration
AUTH0_DOMAIN=your-auth0-domain.auth0.com
AUTH0_API_AUDIENCE=your-api-identifier

# CORS Configuration (optional)
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

### 3. Database Setup

Make sure PostgreSQL is running and create the database:

```sql
CREATE DATABASE travel_planner;
```

The application will automatically create the required tables on first run.

### 4. Auth0 Configuration

1. Create an Auth0 account and application
2. Set up an API in Auth0
3. Configure the following in your Auth0 dashboard:
   - **Domain**: Your Auth0 domain
   - **API Audience**: Your API identifier
   - **Allowed Callback URLs**: Your frontend URLs
   - **Allowed Origins**: Your frontend domains

### 5. Run the Application

```bash
python run.py
```

The application will start on `http://localhost:5000` by default.

## API Endpoints

### Public Endpoints

- `GET /api/public` - Public endpoint (no authentication required)
- `GET /api/health` - Health check endpoint

### Protected Endpoints

All protected endpoints require a valid JWT token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

- `GET /api/private` - Protected endpoint requiring authentication
- `GET /api/profile` - Get or create user profile

## Authentication

The application uses Auth0 for authentication. To access protected endpoints:

1. Obtain a JWT token from Auth0
2. Include the token in the Authorization header:
   ```
   Authorization: Bearer <jwt-token>
   ```

## Development

### Running in Development Mode

```bash
export FLASK_ENV=development
python run.py
```

### Database Migrations

The application uses Flask-SQLAlchemy with automatic table creation. For production, consider using Flask-Migrate for database migrations.

### Testing

To test the API endpoints:

```bash
# Test public endpoint
curl http://localhost:5000/api/public

# Test protected endpoint (requires valid JWT)
curl -H "Authorization: Bearer <your-jwt-token>" http://localhost:5000/api/private
```

## Production Deployment

1. Set `FLASK_ENV=production` in your environment
2. Use a production WSGI server like Gunicorn:
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:8000 run:app
   ```
3. Configure your web server (Nginx) to proxy requests to the Flask application
4. Set up SSL certificates for HTTPS
5. Configure proper database connection pooling

## Security Considerations

- Always use HTTPS in production
- Keep your Auth0 credentials secure
- Use strong, unique secret keys
- Regularly update dependencies
- Implement rate limiting for production use
- Use environment variables for all sensitive configuration

## Troubleshooting

### Common Issues

1. **Database Connection Error**: Ensure PostgreSQL is running and the database exists
2. **Auth0 Token Validation Error**: Check your Auth0 domain and audience configuration
3. **CORS Issues**: Verify your CORS_ORIGINS configuration matches your frontend URL

### Logs

The application logs errors and important events. Check the console output for debugging information.

## Contributing

1. Follow PEP 8 style guidelines
2. Add docstrings to all functions and classes
3. Write tests for new features
4. Update documentation as needed
