import os

bind = f"0.0.0.0:{os.environ.get('PORT', '10000')}"
workers = 2  # Ajusta según los recursos disponibles
timeout = 300
graceful_timeout = 120
module = 'core.wsgi:application'