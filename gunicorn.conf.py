import os

bind = '0.0.0.0:' + os.getenv("PORT", "4000")
workers = 2  # Ajusta según los recursos disponibles
timeout = 300
graceful_timeout = 120
module = 'core.wsgi:application'