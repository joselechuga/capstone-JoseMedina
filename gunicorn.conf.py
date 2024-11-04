import os

port = os.environ.get("PORT", "10000")  # Render especifica el puerto en una variable de entorno
command = f"gunicorn core.wsgi:application --bind 0.0.0.0:{port} --env WEB_CONCURRENCY=2"
os.system(command)
