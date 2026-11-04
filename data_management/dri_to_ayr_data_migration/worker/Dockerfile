FROM public.ecr.aws/lambda/python:3.14@sha256:e89dde43705d09d82b4b6a697cf82c2d89869406803ee39d25d2e81928267140

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

COPY handler.py worker/handler.py
COPY dri_to_ayr_csv.py worker/dri_to_ayr_csv.py

CMD ["worker.handler.lambda_handler"]
