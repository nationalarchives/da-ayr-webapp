FROM public.ecr.aws/lambda/python:3.14

WORKDIR ${LAMBDA_TASK_ROOT}

RUN dnf update -y openssl && \
    dnf clean all && \
    rm -rf /var/cache/dnf

RUN pip install --no-cache-dir --upgrade pip

RUN rm -f /usr/local/bin/aws-lambda-rie

RUN mkdir -p worker

COPY handler.py worker/handler.py
COPY dri_to_ayr_csv.py worker/dri_to_ayr_csv.py

CMD ["worker.handler.lambda_handler"]
