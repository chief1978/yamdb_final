#/bin/sh
# build images, add key --build for force rebuilding images
docker-compose up -d --build
# make migrate
docker-compose exec web python manage.py migrate
# Create admin
docker-compose exec web python manage.py createsuperuser
# Collect static
docker-compose exec web python manage.py collectstatic --no-input