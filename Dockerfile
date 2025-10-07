# Build stage for Node.js assets
FROM node:24-slim AS node-builder

WORKDIR /app

COPY package*.json ./

RUN npm ci

COPY app/static/src app/static/src

RUN npm run build

# Production stage
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    openssl \
    curl \
    tesseract-ocr \
    antiword \
    libreoffice \
    && rm -rf /var/lib/apt/lists/*

RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:$PATH"

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false

RUN poetry install --no-root

COPY . .

COPY --from=node-builder /app/app/static/src/css app/static/src/css

RUN openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365 \
    -subj "/C=GB/ST=England/L=London/O=Test/CN=DNS:localhost,IP:127.0.0.1"

EXPOSE 5000

CMD ["poetry", "run", "python", "-m", "flask", "--app", "main_app:app", "run", "--host=0.0.0.0", "--port=5000"]
