FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

# Install system dependencies without interactive prompts
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements file
COPY pyproject.toml ./

# Устанавливаем uv для управления зависимостями
RUN pip install uv

# Устанавливаем зависимости в систему (без виртуального окружения)
RUN uv pip install --system -r pyproject.toml

# Copy project files
COPY . .

RUN chmod +x /app/prestart.sh /app/test_entry.sh

EXPOSE 8000

CMD ["/app/prestart.sh"]