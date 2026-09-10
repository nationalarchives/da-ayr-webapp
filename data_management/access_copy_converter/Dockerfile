FROM python:3.14-slim@sha256:cad9a2c871761c413caa6fdd6441c783451e740a48aaeba60ae62a8b53525ef6

# Install system dependencies including LibreOffice
RUN apt-get update && apt-get install -y --no-install-recommends \
    libreoffice \
    libreoffice-writer \
    libreoffice-calc \
    libreoffice-java-common \
    default-jre \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy the Python script
COPY access_copy_converter/ /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r /app/requirements.txt

# Set working directory
WORKDIR /app

RUN useradd --create-home --shell /usr/sbin/nologin appuser \
    && chown -R appuser:appuser /app

USER appuser


# Command to run the script
CMD ["python", "main.py"]
