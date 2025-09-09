# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Development Commands

### Environment Setup
```bash
# Create virtual environment (if not exists)
python -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Database Management
```bash
# Create and run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### Development Server
```bash
# Run development server
python manage.py runserver

# Run on specific port
python manage.py runserver 8080
```

### Static Files
```bash
# Collect static files (for production)
python manage.py collectstatic

# Collect static files without prompts
python manage.py collectstatic --no-input
```

### Testing
```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test app

# Run with verbose output
python manage.py test --verbosity=2
```

### Django Shell and Admin
```bash
# Open Django shell
python manage.py shell

# Access admin interface at http://localhost:8000/admin/
```

### Production Build
```bash
# Make build script executable (if needed)
chmod +x build.sh

# Run the build script (installs deps, collects static, runs migrations)
./build.sh
```

### Deployment
```bash
# For Render.com deployment (uses render.yaml configuration)
# The build.sh script runs automatically during deployment

# For local production testing
DJANGO_ENV=production python manage.py runserver

# Production server with Gunicorn
gunicorn web_messenger.wsgi:application
```

## Architecture Overview

### Project Structure
This is a Django web messaging application with the following key architecture:

- **Project Root**: `web_messenger/` - Main Django project configuration
- **Main App**: `app/` - Contains all application logic, models, views, and templates
- **Database**: SQLite3 for development, PostgreSQL support for production via environment variables

### Core Models (`app/models.py`)
- **UserProfile**: Extends Django's User model with nickname, avatar emoji, online status, and theme preferences
- **Contact**: Manages user contact relationships (many-to-many through explicit contacts)
- **Message**: Stores messages between users with status tracking (sent/delivered/read)

### Key Views (`app/views.py`)
- **Authentication Flow**: `register`, `user_login`, `user_logout`, `profile_setup`
- **Chat Interface**: `chat` - Combined contact list and messaging interface
- **API Endpoints**: `get_messages` - JSON API for real-time message updates
- **Contact Management**: `add_contact` for adding new contacts

### URL Structure (`app/urls.py`)
- `/` - Home page (redirects to chat if authenticated)
- `/register/` - User registration
- `/login/` - User login
- `/chat/` - Main chat interface with optional `?contact_id=` parameter
- `/profile/` - Profile update page
- `/api/messages/` - JSON API for message retrieval

### Forms (`app/forms.py`)
- **SimpleRegistrationForm**: Custom registration with nickname and emoji selection
- **SimpleLoginForm**: Supports login via nickname or username
- **MessageForm**: Basic message composition
- **ProfileUpdateForm**: User profile customization

### Template Structure
Templates are located in `app/templates/app/` and include:
- Modern responsive design with base templates
- Chat interface with real-time messaging capabilities
- User registration and authentication pages

### Key Features
- **Real-time Chat**: Message status tracking and real-time updates
- **Contact Management**: Auto-contact addition when messaging users
- **User Profiles**: Custom nicknames, avatar emojis, and theme preferences
- **Online Status**: Tracks user online/offline status
- **Production Ready**: Environment variable configuration for deployment

### Development Notes
- Uses WhiteNoise for static file serving in production
- Supports both SQLite (development) and PostgreSQL (production) via DATABASE_URL
- Password validation requires minimum 8 characters
- Auto-creates UserProfile when User is created via Django signals
- Production settings activated via `DJANGO_ENV=production` environment variable
- Uses dj-database-url for database configuration parsing
- Configured for Render.com deployment with render.yaml
- No static files directory in app (uses Django defaults with WhiteNoise)

### Key Dependencies
- Django 5.2.6 - Web framework
- WhiteNoise 6.5.0 - Static file serving
- Gunicorn 21.2.0 - Production WSGI server
- dj-database-url 2.1.0 - Database URL parsing
- psycopg2-binary 2.9.9 - PostgreSQL adapter
