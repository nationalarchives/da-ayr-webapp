FROM python:3.15.1-slim@sha256:533b0b2f9b5d46fd097091cf826f27902f1d6c3bca714b6dc74551356aa97a51

# Install system dependencies including LibreOffice
RUN apt-get update && \
    apt-get upgrade -y --no-install-recommends && \
    apt-get install -y --no-install-recommends \
    libsqlite3-0 \
    perl-base \
    libc6 \
    libc-bin \
    libreoffice \
    libreoffice-writer \
    libreoffice-calc \
    libreoffice-java-common \
    default-jre \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy the Python script
COPY access_copy_converter/ /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r /app/requirements.txt

# Set working directory
WORKDIR /app

# Enforce macro blocking for every profile, including trusted documents.
COPY --chmod=644 libreoffice-macro-security.xcd /usr/lib/libreoffice/share/registry/ayr-macro-security.xcd

RUN useradd --create-home --shell /usr/sbin/nologin appuser \
    && chown -R appuser:appuser /app

USER appuser


# Command to run the script
CMD ["python", "main.py"]
