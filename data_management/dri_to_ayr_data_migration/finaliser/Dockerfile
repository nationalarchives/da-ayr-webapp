FROM public.ecr.aws/lambda/python:3.14@sha256:1477a590b2104bb8ae2d64f3967d8dde76792ab3922bcc0d56c6621425cb2129

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
