# Python 3.13-slim
FROM python@sha256:5f1cdbcab9a50594a79502dd73e885456d2a2fc31f1a1fa18484815b37ee9152

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
