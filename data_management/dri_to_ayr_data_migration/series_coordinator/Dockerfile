FROM public.ecr.aws/lambda/python:3.14@sha256:5d318087bb422519012c82ddcf4f0057f5e53aed0ff79989a9da0acd53c3fa50

WORKDIR ${LAMBDA_TASK_ROOT}

RUN rm -f /usr/local/bin/aws-lambda-rie

COPY handler.py .

CMD ["handler.lambda_handler"]
