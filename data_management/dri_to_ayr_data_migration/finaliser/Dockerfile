FROM public.ecr.aws/lambda/python:3.14@sha256:486b444fbc2079290e331eb86c4e1a5f11eb72873bd2ea883b177a1cd070ed09

ARG AL2023_RELEASE=2023.12.20260928

RUN dnf clean all && \
  dnf upgrade -y && \
    dnf install -y \
      curl-minimal \
      libcurl-minimal \
      openssl-fips-provider-latest \
      openssl-snapsafe-libs && \
    dnf clean all && \
    rm -rf /var/cache/dnf

RUN rm -f /usr/local/bin/aws-lambda-rie

COPY handler.py .

CMD ["handler.lambda_handler"]
