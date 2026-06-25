# Python 3.13-slim
FROM python@sha256:4d7dd74c5b2d3151fe58eb8ecc9c56be13471a240ce5423ba765b04f8f95ebe8

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
