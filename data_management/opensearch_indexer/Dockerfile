FROM python:3.14.8-slim@sha256:a2b82f3c48559aa0a8446d9af49826b6e2b2016f4cd2afabfe6013ec53729170

# renovate: datasource=deb depName=python3-dev
ARG PYTHON3_DEV_VERSION=3.13.5-1
# renovate: datasource=deb depName=libxml2-dev
ARG LIBXML2_DEV_VERSION=2.12.7+dfsg+really2.9.14-2.1+deb13u3
# renovate: datasource=deb depName=libxslt1-dev
ARG LIBXSLT1_DEV_VERSION=1.1.35-1.2+deb13u3
# renovate: datasource=deb depName=antiword
ARG ANTIWORD_VERSION=0.37-17
# renovate: datasource=deb depName=unrtf
ARG UNRTF_VERSION=0.21.10-clean-1
# renovate: datasource=deb depName=poppler-utils
ARG POPPLER_UTILS_VERSION=25.03.0-5+deb13u4
# renovate: datasource=deb depName=tesseract-ocr
ARG TESSERACT_OCR_VERSION=5.5.0-1+b1
# renovate: datasource=deb depName=flac
ARG FLAC_VERSION=1.5.0+ds-2
# renovate: datasource=deb depName=ffmpeg
ARG FFMPEG_VERSION=7:7.1.5-0+deb13u1
# renovate: datasource=deb depName=lame
ARG LAME_VERSION=3.100-6+b3
# renovate: datasource=deb depName=libmad0
ARG LIBMAD0_VERSION=0.15.1b-11+b1
# renovate: datasource=deb depName=libsox-fmt-mp3
ARG LIBSOX_FMT_MP3_VERSION=14.4.2+git20190427-5+b3
# renovate: datasource=deb depName=sox
ARG SOX_VERSION=14.4.2+git20190427-5+b3
# renovate: datasource=deb depName=libjpeg-dev
ARG LIBJPEG_DEV_VERSION=1:2.1.5-4
# renovate: datasource=deb depName=swig
ARG SWIG_VERSION=4.3.0-1
# renovate: datasource=deb depName=libreoffice
ARG LIBREOFFICE_VERSION=4:25.2.3-2+deb13u8
# renovate: datasource=deb depName=libreoffice-java-common
ARG LIBREOFFICE_JAVA_COMMON_VERSION=4:25.2.3-2+deb13u8
# renovate: datasource=deb depName=default-jre
ARG DEFAULT_JRE_VERSION=2:1.21-76
# renovate: datasource=deb depName=libsqlite3-0
ARG LIBSQLITE3_0_VERSION=3.46.1-7+deb13u2
# renovate: datasource=deb depName=perl-base
ARG PERL_BASE_VERSION=5.40.1-6+deb13u1
# renovate: datasource=deb depName=libpcre2-8-0
ARG LIBPCRE2_8_0_VERSION=10.46-1~deb13u3

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libsqlite3-0=${LIBSQLITE3_0_VERSION} \
    perl-base=${PERL_BASE_VERSION} \
    libpcre2-8-0=${LIBPCRE2_8_0_VERSION} \
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
