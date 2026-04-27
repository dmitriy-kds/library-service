# Library Service API

API service for library management built with Django REST Framework.

## Features
- Library service with Book and Borrowing models
- Custom user model with email as username
- JWT token authentication and permissions for enhanced security
- Functionality to borrow and return books
- Borrowing filtering by status for users, borrowing filtering by used_id for admins
- Admin panel for managing users, book and borrowing data
- Telegram notifications on borrowing creation
- API documentation via Swagger UI

## Installing / Getting started

Run via Docker:
Docker should be installed
```shell
git clone https://github.com/dmitriy-kds/library-service
cd library-service
cp .env.sample .env  # fill in the required values
docker-compose up --build
```
The app will be available at http://localhost:8000/
API documentation: http://localhost:8000/api/doc/swagger/
To create a superuser:
```shell
docker-compose exec app python manage.py createsuperuser

```

Run locally:
Install PostgresSQL and create db
```shell
git clone https://github.com/dmitriy-kds/library-service
cd library-service
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.sample .env  # fill in the required values
python manage.py migrate
python manage.py runserver
```
To create a superuser:
```shell
python manage.py createsuperuser

```
