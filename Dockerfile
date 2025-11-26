FROM python:3.13-slim@sha256:193fdd0bbcb3d2ae612bd6cc3548d2f7c78d65b549fcaa8af75624c47474444d

WORKDIR /docker_app

# Install system dependencies including Node.js (cached layer)
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    openssl \
    curl \
    tesseract-ocr \
    antiword \
    libreoffice

RUN curl -fsSL https://deb.nodesource.com/setup_25.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry (cached layer)
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:$PATH"

# Copy Python dependency files first for better caching
COPY pyproject.toml poetry.lock /docker_app/
RUN poetry config virtualenvs.create false && \
    poetry install --no-root --no-cache

# Copy Node.js dependency files and install
COPY package*.json /docker_app/
RUN npm ci
COPY app/static/src/scss /docker_app/app/static/src/scss
# Build CSS files before copying the rest of the app as
# we won't update them as often as other source files
RUN npm run build

# Preserve CSS files as copying app directory will overwrite them
RUN cp -r /docker_app/app/static/src/css /tmp/css_backup
COPY app/ /docker_app/app
COPY configs/ /docker_app/configs
COPY main_app.py .flaskenv /docker_app/
# Restore the built CSS files
RUN cp -r /tmp/css_backup /docker_app/app/static/src/css


ENV FLASK_ENV=development
ENV FLASK_DEBUG=1
ENV PYTHONUNBUFFERED=1

RUN openssl req -x509 -newkey rsa:2048 -nodes -out /docker_app/cert.pem -keyout /docker_app/key.pem -days 365 -subj '/C=GB/ST=Test/L=Test/O=Test/CN=localhost'

EXPOSE 5000

CMD ["poetry", "run", "flask", "run", "--host=0.0.0.0", "--port=5000", "--debug"]
