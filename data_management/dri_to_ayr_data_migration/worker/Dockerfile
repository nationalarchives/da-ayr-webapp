FROM public.ecr.aws/lambda/python:3.14@sha256:486b444fbc2079290e331eb86c4e1a5f11eb72873bd2ea883b177a1cd070ed09

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
