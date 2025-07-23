python manage.py migrate --noinput

python manage.py collectstatic --no-input

# forward commands to CMD
exec "$@"
