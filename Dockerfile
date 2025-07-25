FROM python:3.12-slim

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

ENV STATIC_ROOT static_root/static
ENV GUNICORN_WORKERS 3

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY ./requirements/requirements.txt /tmp/requirements.txt

RUN pip install --no-cache-dir --no-deps -v -r /tmp/requirements.txt

# TODO: use spearate user instead of root. Mounting the dirs were overriding the user permission.
# RUN groupadd --gid 30000 app_grp \
#    && useradd --uid 30001 --gid app_grp --shell /bin/bash -c 'app user' -m app_usr \
#    && chown -R app_usr:app_grp /app

#COPY --chown=app_usr:app_grp . .
COPY . .

RUN chmod +x entrypoint.sh
#    && mkdir -p /app/static_root \
#    && chown -R app_usr:app_grp /app/static_root

EXPOSE 8000

#USER app_usr

ENTRYPOINT ["sh", "/app/entrypoint.sh"]
CMD ["sh", "-c", "gunicorn --bind :8000 --workers ${GUNICORN_WORKERS} --limit-request-line=5000 --timeout 120 --preload --error-logfile ./logs/gunicorn-error.log lunchlog.wsgi"]
