FROM public.ecr.aws/lambda/python:3.14@sha256:af5e126c7bf423607e0ed9f96384186d108346d9df6a5d8e913aa6c2f1746308

WORKDIR ${LAMBDA_TASK_ROOT}

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

RUN mkdir -p worker

COPY csv_schema.py .
COPY worker/handler.py worker/handler.py
COPY worker/dri_to_ayr_csv.py worker/dri_to_ayr_csv.py

CMD ["worker.handler.lambda_handler"]
