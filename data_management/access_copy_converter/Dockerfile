FROM python:3.14-slim@sha256:cad9a2c871761c413caa6fdd6441c783451e740a48aaeba60ae62a8b53525ef6

# renovate: datasource=repology depName=debian_13/libreoffice versioning=loose
ARG LIBREOFFICE_VERSION=4:25.2.3-2+deb13u6
# renovate: datasource=repology depName=debian_13/libreoffice-writer versioning=loose
ARG LIBREOFFICE_WRITER_VERSION=4:25.2.3-2+deb13u6
# renovate: datasource=repology depName=debian_13/libreoffice-calc versioning=loose
ARG LIBREOFFICE_CALC_VERSION=4:25.2.3-2+deb13u6
# renovate: datasource=repology depName=debian_13/libreoffice-java-common versioning=loose
ARG LIBREOFFICE_JAVA_COMMON_VERSION=4:25.2.3-2+deb13u6
# renovate: datasource=repology depName=debian_13/default-jre versioning=loose
ARG DEFAULT_JRE_VERSION=2:1.21-76
# renovate: datasource=repology depName=debian_13/libsqlite3-0 versioning=loose
ARG LIBSQLITE3_0_VERSION=3.46.1-7+deb13u2
# renovate: datasource=repology depName=debian_13/perl-base versioning=loose
ARG PERL_BASE_VERSION=5.40.1-6+deb13u1
# renovate: datasource=repology depName=debian_13/libpcre2-8-0 versioning=loose
ARG LIBPCRE2_8_0_VERSION=10.46-1~deb13u2
# renovate: datasource=repology depName=debian_13/libc6 versioning=loose
ARG LIBC6_VERSION=2.41-12+deb13u4
# renovate: datasource=repology depName=debian_13/libc-bin versioning=loose
ARG LIBC_BIN_VERSION=2.41-12+deb13u4

# Install system dependencies including LibreOffice
RUN apt-get update && apt-get install -y --no-install-recommends \
    libsqlite3-0=${LIBSQLITE3_0_VERSION} \
    perl-base=${PERL_BASE_VERSION} \
    libpcre2-8-0=${LIBPCRE2_8_0_VERSION} \
    libc6=${LIBC6_VERSION} \
    libc-bin=${LIBC_BIN_VERSION} \
    libreoffice=${LIBREOFFICE_VERSION} \
    libreoffice-writer=${LIBREOFFICE_WRITER_VERSION} \
    libreoffice-calc=${LIBREOFFICE_CALC_VERSION} \
    libreoffice-java-common=${LIBREOFFICE_JAVA_COMMON_VERSION} \
    default-jre=${DEFAULT_JRE_VERSION} \
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
