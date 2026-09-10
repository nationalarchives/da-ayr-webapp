FROM public.ecr.aws/lambda/python:3.14@sha256:cc414500554c7613b30fe072c142822283f6fbe5f3e875071769581e4cf638e0

WORKDIR ${LAMBDA_TASK_ROOT}

RUN rm -f /usr/local/bin/aws-lambda-rie

COPY handler.py .

CMD ["handler.lambda_handler"]
