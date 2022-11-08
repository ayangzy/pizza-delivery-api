release: python manage.py migrate --no-input
web: gunicorn pizza.wsgi.application --log-file -