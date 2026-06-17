# Python 3.13-slim
FROM python@sha256:4d7dd74c5b2d3151fe58eb8ecc9c56be13471a240ce5423ba765b04f8f95ebe8

# Install system dependencies
RUN apt-get update && apt-get -y upgrade && apt-get install -y --no-install-recommends \
    python3-dev \
    libxml2-dev libxslt1-dev \
    antiword unrtf poppler-utils tesseract-ocr \
    flac ffmpeg lame libmad0 libsox-fmt-mp3 sox \
    libjpeg-dev swig \
    libreoffice \
    libreoffice-java-common \
    default-jre \
    && apt-get clean

# Set working directory
WORKDIR /app

# Copy dependencies
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

COPY opensearch_indexer/ ./opensearch_indexer

# Run main.py
CMD ["python", "-m", "opensearch_indexer.index_consignment.main"]
