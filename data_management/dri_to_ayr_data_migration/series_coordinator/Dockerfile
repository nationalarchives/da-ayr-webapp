FROM public.ecr.aws/lambda/python@sha256:67b32eb858d2124326e3887fa825a0db934cbbd22f2b0ce489ee1def49020cfe

WORKDIR ${LAMBDA_TASK_ROOT}

RUN pip install --no-cache-dir --upgrade pip

RUN rm -f /usr/local/bin/aws-lambda-rie

COPY handler.py .

CMD ["handler.lambda_handler"]
