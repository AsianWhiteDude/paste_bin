# Project overview
Developed a web application called "Pastebin," which allows users to save blocks of text and share them via a unique link. During the creation of this application, I achieved the following goals:

- Implemented the project using the Django framework. I used PostgreSQL as the database and organized object storage in S3 Storage.
- Developed a separate distributed key generation service using Flask and Celery for handling asynchronous tasks.
- Wrote a service for automatic record cleanup.
- Set up Redis as a message broker for Celery and as a cache for frequently accessed data.
- Created a Dockerfile and Docker Compose configuration, and configured Nginx along with Gunicorn.
- Technologies used include Django, PostgreSQL, Docker, Celery, Redis, Nginx, RabbitMQ, and Flask.

You can find the architecture of the application here: [Architecture Diagram](https://miro.com/app/board/uXjVKuXjHlw=/).

# Cloning a repository

Cloning: Clone your private copy of the repository to your local machine:

```
git clone https://github.com/AsianWhiteDude/paste_bin.git
cd paste_bin
```

# Deploy
Docker Compose: Docker Compose is used to deploy the application.

```
docker compose up -d
```

This will start the container in the background with the specified services.

## Post-deploy update:

To apply changes on upgrade:

```
docker compose down
```
Delete all images and volumes

```
docker compose up -d
```

```
docker compose up -d
```
