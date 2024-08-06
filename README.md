## Project overview
Developed a web application called "Pastebin," which allows users to save blocks of text and share them via a unique link. During the creation of this application, I achieved the following goals:

- Implemented the project using the Django framework. I used PostgreSQL as the database and organized object storage in S3 Storage.
- Developed a separate distributed key generation service using Flask and Celery for handling asynchronous tasks.
- Wrote a service for automatic record cleanup.
- Set up Redis as a message broker for Celery and as a cache for frequently accessed data.
- Created a Dockerfile and Docker Compose configuration, and configured Nginx along with Gunicorn.
- Technologies used include Django, PostgreSQL, Docker, Celery, Redis, Nginx, and Flask.

You can find the architecture of the application here: [Architecture Diagram](https://miro.com/app/board/uXjVKuXjHlw=/).
