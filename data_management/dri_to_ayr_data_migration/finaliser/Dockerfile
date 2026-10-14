FROM public.ecr.aws/lambda/python:3.14@sha256:1477a590b2104bb8ae2d64f3967d8dde76792ab3922bcc0d56c6621425cb2129

ARG AL2023_RELEASE=2023.12.20260928
ARG OPENSSL_VERSION=1:3.5.8-1.amzn2023.0.1
ARG CURL_VERSION=8.21.0-5.amzn2023.0.2

RUN dnf clean all && \
  dnf upgrade -y --releasever="${AL2023_RELEASE}" && \
    dnf install -y \
      --releasever="${AL2023_RELEASE}" \
      "curl-minimal-${CURL_VERSION}" \
      "libcurl-minimal-${CURL_VERSION}" \
      "openssl-fips-provider-latest-${OPENSSL_VERSION}" \
      "openssl-snapsafe-libs-${OPENSSL_VERSION}" && \
    dnf clean all && \
    rm -rf /var/cache/dnf

RUN rm -f /usr/local/bin/aws-lambda-rie

COPY handler.py .

CMD ["handler.lambda_handler"]
