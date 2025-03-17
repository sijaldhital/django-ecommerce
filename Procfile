release: python manage.py migrate  
web: gunicorn ecommerce.wsgi --bind 0.0.0.0:$PORT --log-file -
