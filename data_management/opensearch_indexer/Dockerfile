# Python 3.13-slim
FROM python@sha256:7aea6827c8787754f99339ffed8cfc41fb09421f9c7d0e77a198b08422a3455e

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
