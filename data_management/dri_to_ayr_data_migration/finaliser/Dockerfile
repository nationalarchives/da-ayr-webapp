FROM public.ecr.aws/lambda/python:3.14@sha256:5d318087bb422519012c82ddcf4f0057f5e53aed0ff79989a9da0acd53c3fa50

ARG AL2023_RELEASE=2023.12.20260914
ARG OPENSSL_VERSION=1:3.5.8-1.amzn2023.0.1

WORKDIR ${LAMBDA_TASK_ROOT}

ARG AL2023_RELEASE=2023.12.20260914
ARG OPENSSL_VERSION=1:3.5.8-1.amzn2023.0.1

RUN dnf clean all && \
    dnf install -y \
      --releasever="${AL2023_RELEASE}" \
      "openssl-fips-provider-latest-${OPENSSL_VERSION}" \
      "openssl-snapsafe-libs-${OPENSSL_VERSION}" && \
    dnf clean all && \
    rm -rf /var/cache/dnf

RUN rm -f /usr/local/bin/aws-lambda-rie

COPY handler.py .

CMD ["handler.lambda_handler"]
