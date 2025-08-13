# Deploying the Emergency Reporting System

This guide provides instructions for deploying the Emergency Reporting System Telegram Mini App to a public server.

## Local Development

For local development and testing, you can run the Django server directly:

```bash
# Run the Django server
python manage.py runserver 0.0.0.0:8000

# Access the app in your browser at:
# http://localhost:8000/?user_id=12345
```

## Deploying to a Public Server

To make the app accessible via Telegram, you need to deploy it on a server with a public URL.

### 1. Deploy on a hosting service

Deploy the app on a hosting service like:
- Heroku
- PythonAnywhere
- DigitalOcean
- AWS
- Google Cloud Platform

Make sure to:
- Install required packages: `pip install -r requirements.txt`
- Run migrations: `python manage.py migrate`
- Configure static files: `python manage.py collectstatic`
- Set up a production-ready server (Gunicorn, uWSGI, etc.) with HTTPS

### 2. Run with your public URL

Once deployed, run the app with your public URL:

```bash
python run_with_custom_url.py --url=https://your-domain.com
```

### 3. Set up the Telegram bot webhook

Configure the webhook for your Telegram bot:

```
https://api.telegram.org/bot<YOUR_TOKEN>/setWebhook?url=https://your-domain.com/telegram/webhook/
```

Replace `<YOUR_TOKEN>` with your actual bot token and `your-domain.com` with your actual domain.

## Using ngrok for temporary testing

If you want to test with a real Telegram bot but don't have a server yet, you can use ngrok:

1. Install ngrok from https://ngrok.com/download

2. Run the Django server:
   ```bash
   python manage.py runserver 0.0.0.0:8000
   ```

3. In another terminal, run ngrok:
   ```bash
   ngrok http 8000
   ```

4. Use the ngrok URL as your WebApp URL:
   ```bash
   # Get a URL like: https://a1b2c3d4.ngrok.io
   export WEBAPP_URL=https://a1b2c3d4.ngrok.io
   python manage.py runserver
   ```

5. Set up the webhook for your bot:
   ```
   https://api.telegram.org/bot<YOUR_TOKEN>/setWebhook?url=https://a1b2c3d4.ngrok.io/telegram/webhook/
   ```

## Security Considerations

- Always use HTTPS in production
- Don't expose the Django DEBUG mode in production
- Set proper ALLOWED_HOSTS in your settings
- Keep your Telegram bot token secret
- Generate a strong SECRET_KEY for Django
- Regularly update dependencies

## Monitoring and Maintenance

- Set up logging
- Monitor server resources
- Create regular backups
- Set up alerts for any failures 