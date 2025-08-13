# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Telegram-based emergency reporting system built with Django that allows users (especially women) to report emergency incidents through a Telegram bot with a mini web app interface. The system supports multi-language functionality (English, Amharic, Afaan Oromo) and provides location-based information on nearby support agencies.

**Project Structure:**
- Main Django project: `emergency_bot/` 
- Legacy bot app: `bot/` (contains older admin interface and models)
- Main manage.py: Located in project root
- Static files: Collected to `staticfiles/` for production

## Development Commands

### Essential Commands

**Development Setup:**
```bash
# Install dependencies
pip install -r requirements.txt

# Database setup
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

**Running the Application:**
```bash
# Start Django development server
python manage.py runserver

# Run Telegram bot with Django management command
python manage.py runbot --webapp-url=http://localhost:8000

# Alternative bot startup methods
python emergency_bot/scripts/run_bot.py
python run_bot_with_language.bat  # Windows batch file
```

**Translation Management:**
```bash
# Update translation files
python manage.py update_translations

# Compile translations
python manage.py update_translations --compile
```

**Production Deployment:**
```bash
# Docker setup
cd emergency_bot/docker
docker-compose up -d

# Set webhook for production
python set_webhook.py
```

### Testing
```bash
# Run Django tests
python manage.py test

# Test specific app
python manage.py test emergency_bot.accounts
```

## Architecture Overview

### Core Components

**Django Apps Structure:**
- `emergency_bot/` - Main project settings and configuration
- `emergency_bot.accounts/` - User profile management with Telegram authentication
- `emergency_bot.reports/` - Incident reporting with encryption for sensitive data
- `emergency_bot.agencies/` - Support agency database and location services
- `emergency_bot.notifications/` - Real-time notifications using Django Channels
- `emergency_bot.frontend/` - Telegram Mini App templates and static files
- `emergency_bot.telegram_bot/` - Bot logic and language bridge
- `bot/` - Legacy admin interface and role management system

**Key Technologies:**
- Django 5.2 with djangorestframework for backend API
- Django Channels for WebSocket real-time features
- SQLite for development (PostgreSQL for production)
- python-telegram-bot v22.0 for Telegram integration
- Telegram Mini App SDK for frontend
- Bootstrap 5 for UI components
- Cryptography (Fernet) for sensitive data encryption
- Celery with Redis for background tasks
- Poetry for dependency management (alternative to pip)

### Critical Architecture Patterns

**Telegram Authentication Flow:**
1. Bot initiates chat and provides web app button
2. Frontend base.html handles Telegram WebApp SDK initialization
3. TelegramAuthMiddleware validates initData from Telegram
4. User authentication persists via UserProfile model

**Multi-language Implementation:**
- Django's i18n framework for templates and Python code
- Custom translation dictionary in `utils/translations.py` for bot messages
- Language preference stored in UserProfile model
- Bot interface language selection via inline keyboards

**Data Encryption:**
- Sensitive report descriptions encrypted using Fernet symmetric encryption
- Encryption key stored in settings.ENCRYPTION_KEY environment variable
- Graceful fallback when encryption unavailable (logs warning but continues)

**Real-time Features:**
- Django Channels with InMemoryChannelLayer for development
- WebSocket consumers in notifications app for status updates
- Redis backend recommended for production scaling

## Development Guidelines

### File Structure Conventions

**Settings Management:**
- Development: `emergency_bot/settings.py` (single file for simplicity)
- Production: Modular settings in `emergency_bot/emergency_bot/settings/` (base.py, dev.py, prod.py)

**Template Organization:**
- Main templates: `emergency_bot/frontend/templates/`
- Bot admin templates: `bot/templates/admin/`
- Shared base template with Telegram WebApp integration

**Static Files:**
- CSS: Custom styles in `emergency_bot/frontend/static/css/styles.css`
- Production: Static files collected to `staticfiles/`
- Development: Additional static files in `static/` directory

### Security Considerations

**Telegram Bot Token:**
- Stored in settings.TELEGRAM_BOT_TOKEN
- **WARNING:** Currently hardcoded in settings.py - should be moved to environment variables

**Data Protection:**
- Sensitive data encryption in reports models using Fernet symmetric encryption
- GDPR compliance fields in UserProfile (data_consent, consent_date)
- CORS configured for Telegram WebApp origins
- Voice notes stored in `media/voice_notes/` with UUID-based organization

**Authentication:**
- Custom TelegramAuthMiddleware for validating Telegram initData
- User authentication via Telegram ID rather than traditional Django auth

### Testing Strategy

**Key Test Areas:**
- Telegram authentication flow validation
- Report encryption/decryption functionality
- Multi-language message translation
- WebSocket notification delivery
- API endpoint security

### Common Development Tasks

**Adding New Languages:**
1. Update LANGUAGES in settings.py
2. Add choice to UserProfile.language field
3. Create locale/<lang>/LC_MESSAGES/ directory structure
4. Add translations to emergency_bot/utils/translations.py TRANSLATIONS dict

**Extending Report Types:**
1. Update incident report model choices in emergency_bot/reports/models.py
2. Update bot command handlers for new types
3. Add translations for new incident types in emergency_bot/utils/translations.py

**Webhook Configuration:**
- Development: Use ngrok or similar tunneling for local testing
- Production: HTTPS endpoint required for Telegram webhooks
- Set webhook via `/telegram/set-webhook/` endpoint or set_webhook.py script

## Environment Variables

**Required for Production:**
- `TELEGRAM_BOT_TOKEN` - Telegram bot authentication token
- `ENCRYPTION_KEY` - 32-byte base64-encoded key for data encryption
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection for channels/celery
- `SECRET_KEY` - Django secret key for cryptographic signing

**Optional:**
- `WEBAPP_URL` - Base URL for the web application
- `DEBUG` - Django debug mode (default: True in current settings)
- `ALLOWED_HOSTS` - List of allowed hosts for Django