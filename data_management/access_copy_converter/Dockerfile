# Python 3.13-slim
FROM python@sha256:311ea5bb79f1a238ee9e38f8d5f09cb3b4b244575cf49e27cf365ea7e60f11d4

# Install system dependencies including LibreOffice
RUN apt-get update && apt-get -y upgrade && apt-get install -y \
    libreoffice \
    libreoffice-writer \
    libreoffice-calc \
    default-jre \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy the Python script
COPY access_copy_converter/ /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r /app/requirements.txt

# Set working directory
WORKDIR /app


# Command to run the script
CMD ["python", "main.py"]
