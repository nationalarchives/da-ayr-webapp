FROM public.ecr.aws/lambda/python:3.14@sha256:27483b5d8a13e85d0f8207706759a30d6a7c89e60aa9d48ec926b445bdc518d2

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
