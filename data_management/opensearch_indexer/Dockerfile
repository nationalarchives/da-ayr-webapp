FROM python:3.14.10-slim@sha256:9aaa474097d094040649f2162a627c0049b408f52138d980916788d80f04802f

# Install system dependencies
RUN apt-get update && \
    apt-get upgrade -y --no-install-recommends && \
    apt-get install -y --no-install-recommends \
    libsqlite3-0 \
    perl-base \
    python3-dev \
    libxml2-dev \
    libxslt1-dev \
    antiword \
    unrtf \
    poppler-utils \
    tesseract-ocr \
    flac \
    ffmpeg \
    lame \
    libmad0 \
    libsox-fmt-mp3 \
    sox \
    libjpeg-dev \
    swig \
    libreoffice \
    libreoffice-java-common \
    default-jre \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy dependencies
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

COPY opensearch_indexer/ ./opensearch_indexer

# Enforce macro blocking for every profile, including trusted documents.
COPY --chmod=644 libreoffice-macro-security.xcd /usr/lib/libreoffice/share/registry/ayr-macro-security.xcd

RUN useradd --create-home --shell /usr/sbin/nologin appuser \
    && chown -R appuser:appuser /app

USER appuser

# Run main.py
CMD ["python", "-m", "opensearch_indexer.index_consignment.main"]
