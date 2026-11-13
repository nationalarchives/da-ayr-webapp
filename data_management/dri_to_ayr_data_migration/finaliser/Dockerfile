FROM public.ecr.aws/lambda/python:3.14@sha256:4b156c6ffbac3793bd5b41bae7573eccb27e9d1987f4e432502231808d24a38f

ARG AL2023_RELEASE=2023.12.20260928

# Patch all base-image packages, then install new ones from latest release since
# the base AWS Lambda image can have packages with known vulnerabilities
# with fixes only available in the latest release
RUN dnf upgrade --refresh -y --releasever=latest && \
    dnf install -y --releasever=latest \
      curl-minimal \
      libcurl-minimal \
      openssl-fips-provider-latest \
      openssl-snapsafe-libs && \
    dnf clean all && \
    rm -rf /var/cache/dnf

RUN rm -f /usr/local/bin/aws-lambda-rie

COPY csv_schema.py .
COPY finaliser/handler.py .

CMD ["handler.lambda_handler"]
