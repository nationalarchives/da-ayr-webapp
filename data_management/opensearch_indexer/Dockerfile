FROM python:3.14-slim@sha256:cad9a2c871761c413caa6fdd6441c783451e740a48aaeba60ae62a8b53525ef6

# renovate: datasource=repology depName=debian_13/python3-dev versioning=loose
ARG PYTHON3_DEV_VERSION=3.13.5-1
# renovate: datasource=repology depName=debian_13/libxml2-dev versioning=loose
ARG LIBXML2_DEV_VERSION=2.12.7+dfsg+really2.9.14-2.1+deb13u3
# renovate: datasource=repology depName=debian_13/libxslt1-dev versioning=loose
ARG LIBXSLT1_DEV_VERSION=1.1.35-1.2+deb13u3
# renovate: datasource=repology depName=debian_13/antiword versioning=loose
ARG ANTIWORD_VERSION=0.37-17
# renovate: datasource=repology depName=debian_13/unrtf versioning=loose
ARG UNRTF_VERSION=0.21.10-clean-1
# renovate: datasource=repology depName=debian_13/poppler-utils versioning=loose
ARG POPPLER_UTILS_VERSION=25.03.0-5+deb13u4
# renovate: datasource=repology depName=debian_13/tesseract-ocr versioning=loose
ARG TESSERACT_OCR_VERSION=5.5.0-1+b1
# renovate: datasource=repology depName=debian_13/flac versioning=loose
ARG FLAC_VERSION=1.5.0+ds-2
# renovate: datasource=repology depName=debian_13/ffmpeg versioning=loose
ARG FFMPEG_VERSION=7:7.1.5-0+deb13u1
# renovate: datasource=repology depName=debian_13/lame versioning=loose
ARG LAME_VERSION=3.100-6+b3
# renovate: datasource=repology depName=debian_13/libmad0 versioning=loose
ARG LIBMAD0_VERSION=0.15.1b-11+b1
# renovate: datasource=repology depName=debian_13/libsox-fmt-mp3 versioning=loose
ARG LIBSOX_FMT_MP3_VERSION=14.4.2+git20190427-5+b3
# renovate: datasource=repology depName=debian_13/sox versioning=loose
ARG SOX_VERSION=14.4.2+git20190427-5+b3
# renovate: datasource=repology depName=debian_13/libjpeg-dev versioning=loose
ARG LIBJPEG_DEV_VERSION=1:2.1.5-4
# renovate: datasource=repology depName=debian_13/swig versioning=loose
ARG SWIG_VERSION=4.3.0-1
# renovate: datasource=repology depName=debian_13/libreoffice versioning=loose
ARG LIBREOFFICE_VERSION=4:25.2.3-2+deb13u6
# renovate: datasource=repology depName=debian_13/libreoffice-java-common versioning=loose
ARG LIBREOFFICE_JAVA_COMMON_VERSION=4:25.2.3-2+deb13u6
# renovate: datasource=repology depName=debian_13/default-jre versioning=loose
ARG DEFAULT_JRE_VERSION=2:1.21-76

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-dev=${PYTHON3_DEV_VERSION} \
    libxml2-dev=${LIBXML2_DEV_VERSION} \
    libxslt1-dev=${LIBXSLT1_DEV_VERSION} \
    antiword=${ANTIWORD_VERSION} \
    unrtf=${UNRTF_VERSION} \
    poppler-utils=${POPPLER_UTILS_VERSION} \
    tesseract-ocr=${TESSERACT_OCR_VERSION} \
    flac=${FLAC_VERSION} \
    ffmpeg=${FFMPEG_VERSION} \
    lame=${LAME_VERSION} \
    libmad0=${LIBMAD0_VERSION} \
    libsox-fmt-mp3=${LIBSOX_FMT_MP3_VERSION} \
    sox=${SOX_VERSION} \
    libjpeg-dev=${LIBJPEG_DEV_VERSION} \
    swig=${SWIG_VERSION} \
    libreoffice=${LIBREOFFICE_VERSION} \
    libreoffice-java-common=${LIBREOFFICE_JAVA_COMMON_VERSION} \
    default-jre=${DEFAULT_JRE_VERSION} \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy dependencies
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

COPY opensearch_indexer/ ./opensearch_indexer

RUN useradd --create-home --shell /usr/sbin/nologin appuser \
    && chown -R appuser:appuser /app

USER appuser

# Run main.py
CMD ["python", "-m", "opensearch_indexer.index_consignment.main"]
