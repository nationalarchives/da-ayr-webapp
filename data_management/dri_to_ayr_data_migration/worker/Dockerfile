FROM public.ecr.aws/lambda/python:3.14@sha256:252cbb0879717b1c049b9f909d86d06d88e129f3208386d7ba1189d535f5f981

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
