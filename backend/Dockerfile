FROM python:3.11-slim

WORKDIR /app
COPY . .

# Cấp quyền thực thi cho entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1


# install system dependencies
RUN apt-get update && apt-get install -y postgresql-client && rm -rf /var/lib/apt/lists/*
RUN apt-get update && apt-get install -y libzbar0

# install python dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
RUN python manage.py makemigrations
RUN python manage.py makemigrations users customers
RUN python manage.py collectstatic --noinput
# Entrypoint sẽ được cấu hình trong docker-compose để chờ Postgres và migrate
# CMD sẽ được override bởi docker-compose

