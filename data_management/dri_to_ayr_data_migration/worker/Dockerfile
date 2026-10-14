FROM public.ecr.aws/lambda/python:3.14@sha256:1477a590b2104bb8ae2d64f3967d8dde76792ab3922bcc0d56c6621425cb2129

WORKDIR ${LAMBDA_TASK_ROOT}

RUN dnf install -y \
      curl-minimal \
      libcurl-minimal \
      openssl-fips-provider-latest \
      openssl-snapsafe-libs && \
    dnf clean all && \
    rm -rf /var/cache/dnf

RUN rm -f /usr/local/bin/aws-lambda-rie

RUN mkdir -p worker

COPY handler.py worker/handler.py
COPY dri_to_ayr_csv.py worker/dri_to_ayr_csv.py

CMD ["worker.handler.lambda_handler"]
