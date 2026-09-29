FROM public.ecr.aws/lambda/python:3.14@sha256:682e029708e21793bda61ec0cd551bec161e8f69d435804be538521c9f6f4b70

ARG AL2023_RELEASE=2023.12.20260914
ARG OPENSSL_VERSION=1:3.5.8-1.amzn2023.0.1
ARG CURL_VERSION=8.21.0-5.amzn2023.0.2

RUN dnf clean all && \
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
