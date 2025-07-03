# Safe Companion

A secure messaging and companion platform with comprehensive authentication, user management, and security features.

## 🏗️ Project Structure

```
safe-companion/
├── app.py                      # Main Flask application
├── db.py                       # Database configuration
├── extensions.py               # Flask extensions
├── requirements.txt            # Dependencies
├── requirements-prod.txt       # Production dependencies
├── docker-compose.yml          # Production Docker setup
├── docker-compose.dev.yml      # Development Docker setup
├── Dockerfile                  # Container build instructions
├── .env.example               # Environment variables template
├── blueprint/                 # Application blueprints
│   ├── auth.py               # Authentication routes
│   ├── booking.py            # Booking functionality
│   ├── browse.py             # Browse functionality
│   ├── messaging.py          # Messaging system
│   ├── models.py             # Database models
│   ├── payment.py            # Payment processing
│   └── profile.py            # User profiles
├── config/                    # Configuration files
├── controllers/               # Business logic controllers
├── data_sources/              # Data access layer
├── entities/                  # Domain entities
├── static/                    # Static assets (CSS, JS, images)
├── templates/                 # HTML templates
├── utils/                     # Utility functions
├── tests/                     # Test suite
│   ├── unit/                 # Unit tests
│   ├── integration/          # Integration tests
│   ├── functional/           # Functional tests
│   └── run_tests.py          # Test runner
├── scripts/                   # Utility scripts
│   ├── setup/                # Setup scripts
│   ├── migrations/           # Database migrations
│   └── debug/                # Debug utilities
├── migrations/                # SQL migration files
├── docs/                      # Documentation
└── nginx/                     # Nginx configuration
```

## 🔐 Security Features

- **Email Verification**: Secure email verification system
- **OTP Authentication**: Phone-based OTP verification
- **Password Security**: Password history, expiration, and complexity requirements
- **Account Lockout**: Protection against brute force attacks
- **User Reporting**: Comprehensive user reporting system
- **Session Management**: Secure session handling

## Prerequisites

Ensure the following are installed on **Windows** before proceeding:

* [Python 3.13](https://www.python.org/downloads/)
* [Docker Desktop](https://www.docker.com/products/docker-desktop/)
* [PostgreSQL Client](https://www.postgresql.org/download/)

## 🚀 Quick Start

### Using Docker (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd safe-companion
   ```

2. **Set up environment variables**
   ```bash
   copy .env.example .env
   # Edit .env file with your configuration
   ```

3. **Start the application**
   ```bash
   # Development mode
   docker-compose -f docker-compose.dev.yml up --build -d
   
   # Production mode
   docker-compose up --build -d
   ```

4. **Access the application**
   - **Main App**: http://localhost:5000
   - **Database UI**: http://localhost:8080 (admin@ssd.local / admin123)

### Manual Setup

1. **Create virtual environment**
   ```bash
   # Windows
   py -3 -m venv .venv
   .venv\Scripts\activate
   
   # Mac/Linux
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   copy .env.example .env
   # Edit .env file with your configuration
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Run all tests
python tests/run_tests.py

# Run specific test types
python tests/run_tests.py unit
python tests/run_tests.py integration
python tests/run_tests.py functional
```

## 📊 Database

### Docker Database Access

```bash
# Connect to PostgreSQL in container
psql -h localhost -p 5432 -U ssd_user -d ssd_database
```

### Database Migration

```bash
# Run database migrations
python scripts/migrations/migrate_database_schema.py
python scripts/migrations/migrate_otp_system.py
python scripts/migrations/migrate_password_security.py
```

## 🔧 Development

### Setup Development Environment

```bash
# Install development dependencies
npm install

# Run static code analysis
npm run lint

# Start development server with hot reload
docker-compose -f docker-compose.dev.yml up --build
```

### Code Quality

```bash
# Run ESLint
docker-compose run --rm eslint

# Run SonarQube analysis
docker-compose -f sonarqube-compose.yml up -d
```

## 📚 Documentation

Comprehensive documentation is available in the `docs/` directory:

- **Implementation Guides**: Feature-specific implementation details
- **Testing Guides**: Testing procedures and verification steps
- **Security Documentation**: Security feature documentation
- **API Documentation**: Endpoint documentation

## 🐳 Docker Commands

```bash
# Build and run (Development)
docker-compose -f docker-compose.dev.yml up --build -d

# Build and run (Production)
docker-compose up --build -d

# Stop containers
docker-compose down

# Complete cleanup
docker-compose down --volumes --rmi all --remove-orphans

# View logs
docker-compose logs -f
```

## 🔒 Security Notes

- Always use HTTPS in production
- Regularly update dependencies
- Monitor application logs
- Use strong environment-specific secrets
- Enable all security features in production

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.