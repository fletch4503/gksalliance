#!/bin/sh
set -e

echo "Waiting for database to be ready..."
python - <<'PY'
import socket, os, time, sys
host = os.getenv('POSTGRES_HOST')
port = int(os.getenv('POSTGRES_PORT'))
timeout = 2
for i in range(60):
	try:
		sock = socket.create_connection((host, port), timeout)
		sock.close()
		print('Database is ready')
		sys.exit(0)
	except Exception as e:
		print(f'Waiting for DB ({host}:{port}): {e}')
		time.sleep(1)
print('Database is not available, exiting')
sys.exit(1)
PY

echo "Running migrations..."
uv run python manage.py makemigrations tasks
uv run python manage.py migrate --noinput

echo "Collecting static (if any)"
uv run python manage.py collectstatic --noinput || true

echo "Creating test data..."
uv run python manage.py create_test_data || true

echo "Starting server using uv run..."
uv run python manage.py runserver 0.0.0.0:8000
