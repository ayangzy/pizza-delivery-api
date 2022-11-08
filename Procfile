release: python3 manage.py migrate --no-input
web: gunicorn pizza.wsgi.application --log-file -