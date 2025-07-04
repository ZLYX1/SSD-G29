---
mode: ask
---
# GitHub Copilot Context

## Project Overview

**Project Name**: Safe Companion  
**Type**: Secure messaging and companion platform  
**Technology Stack**: Flask, Python, PostgreSQL, Docker, Bootstrap  
**Purpose**: Comprehensive authentication, user management, and security features

## Project Structure

```
safe-companion/
├── app.py                      # Main Flask application
├── db.py                       # Database configuration
├── extensions.py               # Flask extensions
├── requirements.txt            # Dependencies
├── blueprint/                  # Application blueprints
│   ├── auth.py                # Authentication routes
│   ├── booking.py             # Booking functionality
│   ├── browse.py              # Browse functionality
│   ├── messaging.py           # Messaging system
│   ├── models.py              # Database models
│   ├── payment.py             # Payment processing
│   ├── profile.py             # User profiles
│   └── rating.py              # Rating system
├── controllers/               # Business logic controllers
├── templates/                 # HTML templates
├── static/                    # Static assets
├── tests/                     # Test suite
├── scripts/                   # Utility scripts
├── migrations/                # SQL migration files
└── docs/                      # Documentation
```

## Key Components

### Authentication System
- **Email verification** with token-based system
- **OTP phone verification** for additional security
- **Password security** with history, expiration, complexity
- **Account lockout** protection against brute force
- **Session management** with secure cookies

### User Roles
- **Seeker**: Users looking for companions
- **Escort**: Service providers
- **Admin**: System administrators

### Core Features
1. **User Registration/Login** with multi-factor authentication
2. **Profile Management** with photo uploads and personal info
3. **Browse System** to view available escorts with filtering
4. **Messaging System** with end-to-end encryption
5. **Booking System** for scheduling appointments
6. **Rating/Review System** for service feedback
7. **Payment Processing** for transactions
8. **Reporting System** for safety and security

## Database Schema

### Key Tables
- **user**: User authentication and basic info
- **profile**: Extended user profile information
- **message**: Secure messaging between users
- **booking**: Appointment scheduling
- **rating**: User ratings and reviews
- **payment**: Transaction records
- **report**: User reporting system

## Current Status & Implementation

### Completed Features ✅
- [x] User authentication (login/register)
- [x] Database setup with PostgreSQL
- [x] Profile management system
- [x] Browse escorts functionality
- [x] Messaging system with privacy controls
- [x] Rating and review system
- [x] Docker containerization
- [x] Basic security features

### Test Data Available
- **Seeker User**: seeker@example.com / password123
- **Escort Users**: 
  - escort1@example.com (Sarah Johnson) / password123
  - escort2@example.com (David Chen) / password123
  - escort3@example.com (Emily Rodriguez) / password123
  - escort4@example.com (Michael Thompson) / password123

### Recent Fixes & Updates
1. **Login Flow Fix**: Resolved redirect issue from /profile to /dashboard
2. **Browse Functionality**: Added test escort profiles and data
3. **Ratings System**: Created missing user_ratings.html template
4. **Messaging Privacy**: Verified secure message isolation between users

## Security Considerations

### Implemented Security Measures
- CSRF protection with tokens
- SQL injection prevention with parameterized queries
- Password hashing with secure algorithms
- Session security with HTTP-only cookies
- Input validation and sanitization
- Account lockout after failed attempts

### Security Best Practices
- Always use HTTPS in production
- Validate all user inputs
- Implement proper error handling
- Log security events
- Regular security audits
- Keep dependencies updated

## Development Environment

### Docker Setup
- **Web Container**: Flask application
- **Database Container**: PostgreSQL
- **Admin Interface**: pgAdmin for database management

### Access Points
- **Main App**: http://localhost:5000
- **Database UI**: http://localhost:8080 (admin@ssd.local / admin123)

### Key Environment Variables
- DATABASE_URL: PostgreSQL connection string
- FLASK_SECRET_KEY: Application secret key
- CSRF_SECRET_KEY: CSRF protection key

## Testing Strategy

### Test Categories
1. **Unit Tests**: Individual component testing
2. **Integration Tests**: Component interaction testing
3. **Functional Tests**: End-to-end feature testing
4. **Security Tests**: Vulnerability assessment

### Key Test Scenarios
- User authentication flows
- Message privacy and isolation
- Profile access controls
- Booking system integrity
- Payment processing security
- Database operation safety

## Known Issues & Technical Debt

### Current Issues
- Favorite button functionality not implemented
- Profile photo upload needs AWS S3 integration
- Real-time messaging could be enhanced
- Payment gateway integration pending

### Future Enhancements
- WebSocket for real-time messaging
- Advanced search and filtering
- Mobile app development
- API rate limiting
- Advanced analytics

## Code Quality Standards

### Python Standards
- Follow PEP8 coding conventions
- Use type hints where appropriate
- Implement proper error handling
- Write comprehensive docstrings

### Database Standards
- Use parameterized queries only
- Implement proper indexing
- Regular backup procedures
- Data migration scripts

### Frontend Standards
- Responsive design with Bootstrap
- Accessible UI components
- Cross-browser compatibility
- Progressive enhancement

## Useful Context for Development

### Common Patterns
- Blueprint-based route organization
- Controller pattern for business logic
- Model-based database operations
- Template inheritance for UI consistency

### Key Files to Reference
- `blueprint/models.py`: Database model definitions
- `app.py`: Main application configuration
- `templates/base.html`: Base template for all pages
- `requirements.txt`: Project dependencies

### Development Workflow
1. Make changes in development environment
2. Test locally with Docker containers
3. Run comprehensive test suite
4. Update documentation as needed
5. Commit with clear messages

## Project Goals & Vision

### Primary Objectives
- Secure companion platform with robust authentication
- Privacy-focused messaging system
- User-friendly interface with modern design
- Scalable architecture for future growth
- Comprehensive security implementation

### Success Metrics
- Secure user authentication (100% coverage)
- Private messaging (verified isolation)
- Responsive design (mobile-first)
- Performance optimization (fast load times)
- Security compliance (industry standards)

---

**Last Updated**: July 3, 2025  
**Status**: Active Development  
**Maintainer**: Development Team