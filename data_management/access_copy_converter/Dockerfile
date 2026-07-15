# Python 3.13-slim
FROM python@sha256:2a8b92a1e9eb6ef2c888eb7e6c91283788c6d613fdc8fc22e12346aff7c4406d

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
