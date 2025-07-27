# LunchLog

LunchLog is a Django-based application for logging lunch receipts, with integrations for AWS S3 (image storage), Celery (background tasks), and Google Places (restaurant data).

## Requirements

- Python 3.12+
- Docker & Docker Compose
- AWS account (for S3 storage)
- Google Places API key

## Setup Using Docker Compose

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd LunchLog
   ```

2. **Configure environment variables:**
   - Copy `env/example.env` to `.env` and fill in required values (AWS credentials, Google API key, Django secret key, etc).

3. **Build and start the containers:**
   ```bash
   docker-compose up --build
   ```
   This will start the Django app, Celery worker, and any other services defined in `docker-compose.yml`.

4. **Create a superuser (optional):**
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

## Running Test Cases

To run all tests:
```bash
# Run inside the web container
docker-compose exec web python manage.py test user_api.tests
```

## Celery Usage

Celery is used for background tasks (e.g., image processing, notifications).
- The worker is started via Docker Compose.
- Tasks are defined in `user_api/tasks.py`.
- To trigger a task, use the Django API or admin interface as appropriate.

## AWS S3 Integration

- Receipt images are uploaded to AWS S3.
- Configure your AWS credentials in the `.env` file:
  - `AWS_ACCESS_KEY_ID`
  - `AWS_SECRET_ACCESS_KEY`
  - `AWS_STORAGE_BUCKET_NAME`
- The Django settings (`lunchlog/settings.py`) should be configured for S3 storage.

## Google Places Integration

- Used to fetch restaurant data.
- Set your Google Places API key in the `.env` file:
  - `GOOGLE_PLACES_API_KEY`
- Integration code is typically in `user_api/utils/common.py` or related modules.

## Useful Commands

- **Start all services:**
  ```bash
  docker-compose up
  ```
- **Stop all services:**
  ```bash
  docker-compose down
  ```
- **View logs:**
  ```bash
  docker-compose logs web
  docker-compose logs celery
  ```

## Folder Structure

- `lunchlog/` - Django project settings
- `user_api/` - Main app (models, views, serializers, tasks)
- `requirements/` - Python dependencies
- `static_root/` - Static files
- `templates/` - HTML templates
- `nginx/` - Nginx config

## Troubleshooting

- Ensure all environment variables are set correctly.
- Check logs in the `logs/` directory for errors.
- For AWS/Google API issues, verify credentials and network access.

---
For more details, see the documentation in each module or contact the project maintainer.
