FROM public.ecr.aws/lambda/python:3.14@sha256:9d8d55436e229d76589dbd239eb3380dc452ecc7a1b043bc6a0f2f1d95514cd1

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
