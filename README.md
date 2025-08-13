# 📘 Telegram Mini App: Emergency Reporting System

**Project Goal:**
Build a Telegram-based mini web app that allows users—especially women—to report emergency incidents (e.g., rape, assault) and access location-based information on nearby support agencies (e.g., police, hospitals, NGOs).

## System Architecture

### Core Components
- **Telegram Bot**: Entry point that initiates chat and loads the web app
- **Multi-language Support**: Bot UI in English, Amharic, and Afaan Oromo via bot buttons
- **Mini App Frontend**: Browser-based interface opened inside Telegram using HTML/CSS/JS
- **Django Backend**: REST API with Django Channels for real-time features
- **SQLite Database**: Lightweight DB for development (PostgreSQL for production)
- **Django Admin**: Panel to manage incident types, agency data, and users

### Technology Stack
- **Backend**: Django + Django REST Framework + Django Channels
- **Database**: SQLite (dev) / PostgreSQL (prod)
- **Real-time Features**: Django Channels + Redis (for WebSockets)
- **Background Tasks**: Celery + Redis
- **Frontend**: HTML/CSS/JavaScript with Telegram WebApp SDK
- **Translation**: Django's internationalization framework + custom translation system
- **Containerization**: Docker + Docker Compose
- **Security**: HTTPS/TLS, CSRF protection, secure authentication

## Project Structure

```
emergency_bot/
├── manage.py
├── emergency_bot/          # Project settings
│   ├── settings/
│   │   ├── base.py
│   │   ├── dev.py
│   │   └── prod.py
│   ├── urls.py
│   ├── asgi.py            # For Channels
│   └── wsgi.py
├── accounts/              # User accounts
│   ├── models.py          # UserProfile
│   └── ...
├── reports/               # Incident reporting
│   ├── models.py          # IncidentReport
│   ├── serializers.py     # DRF serializers
│   └── ...
├── agencies/              # Support agencies
│   ├── models.py          # Agency
│   └── ...
├── notifications/         # Real-time alerts
│   ├── consumers.py       # WebSocket consumers
│   └── ...
├── telegram_bot/          # Telegram bot configuration
├── frontend/              # Mini App frontend
├── templates/
├── static/
├── media/
├── docker/                # Docker configuration
│   ├── Dockerfile
│   └── docker-compose.yml
├── requirements/
│   ├── base.txt
│   ├── dev.txt
│   └── prod.txt
└── tests/                 # Test suite
```

## Development Phases

### Phase 1: Foundation (2-3 weeks)
- Project setup with modular structure
- Core models (UserProfile, IncidentReport, Agency)
- Basic authentication and user registration
- Initial Django Admin customization

### Phase 2: API Development (2-3 weeks)
- REST API endpoints for incident reporting
- Agency information retrieval based on location
- Integration with Telegram Bot

### Phase 3: Frontend Mini App (2-3 weeks)
- Telegram Mini App frontend implementation
- Location services integration
- Voice note recording functionality
- Multi-language support (English, Amharic, Afaan Oromo)

### Phase 4: Real-time Features (1-2 weeks)
- WebSocket integration for real-time alerts
- Notification system for status updates
- Background tasks for data processing

### Phase 5: Security & Deployment (1-2 weeks)
- Security hardening (HTTPS, data encryption)
- GDPR compliance measures
- Containerization and deployment setup
- Production environment configuration

## Security & Privacy Features

- **GDPR Compliance**: Data minimization, transparent collection
- **Encryption**: Sensitive data encrypted at rest
- **Authentication**: Secure token-based authentication
- **Authorization**: Role-based access control
- **HTTPS**: TLS encryption for all communications
- **Audit Logging**: Track critical system actions

## Testing Strategy

- **Unit Tests**: Individual components and models
- **Integration Tests**: End-to-end workflows
- **Security Tests**: Vulnerability scanning
- **Performance Tests**: System under load
- **User Acceptance Testing**: Real-world scenarios

## Deployment

- Docker containers for consistent environments
- CI/CD pipeline for automated testing and deployment
- Environment-specific configurations
- Backup and disaster recovery plans

## Key Features

- Voice and text incident reporting
- Location-based agency search
- Real-time status updates and notifications
- **Multi-language support through bot interface (English, Amharic, Afaan Oromo)**
- Admin management of agencies and reports
- Secure data handling and privacy protection 

## Running the Project

### Prerequisites

- Python 3.8+
- Django 4.2+
- Telegram Bot Token (from @BotFather)

### Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd emergency_bot
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up the database:
   ```
   python manage.py migrate
   ```

5. Create a superuser:
   ```
   python manage.py createsuperuser
   ```

### Running the Django Server

```
python manage.py runserver
```

The server will start at http://localhost:8000/

### Running the Telegram Bot

There are two ways to run the Telegram bot:

#### 1. Using the management command:

```
python manage.py runbot --webapp-url=http://localhost:8000
```

#### 2. Using the script:

```
python emergency_bot/scripts/run_bot.py
```

You can set the `WEBAPP_URL` environment variable to specify the URL where your Django server is running:

```
# On Linux/Mac
export WEBAPP_URL=http://localhost:8000
python emergency_bot/scripts/run_bot.py

# On Windows
set WEBAPP_URL=http://localhost:8000
python emergency_bot/scripts/run_bot.py
```

### Managing Translations

The system supports multiple languages through bot buttons. To update translations:

1. Edit the translation files in `emergency_bot/utils/translations.py` for bot messages
2. For Django-based translations, use the management command:
   ```
   python manage.py update_translations
   ```
3. After updating the .po files in the locale directory, compile them:
   ```
   python manage.py update_translations --compile
   ```

See `LANGUAGE_SUPPORT.md` for more details on the translation system.

### Setting up Webhook (Production)

For production, you should set up a webhook for the Telegram bot:

1. Make sure your server is accessible via HTTPS
2. Visit the following URL to set up the webhook:
   ```
   https://your-domain.com/telegram/set-webhook/
   ```

### Testing the Bot

1. Start a chat with your bot on Telegram
2. Send the `/start` command
3. Use the "Open Emergency App" button to access the mini app 