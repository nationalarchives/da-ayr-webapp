FROM public.ecr.aws/lambda/python:3.12@sha256:cd10f0b787a6a2adebb2bb0dfa21e1285eb095305abb915b16288c56d21e0d48

WORKDIR ${LAMBDA_TASK_ROOT}

RUN rm -f /usr/local/bin/aws-lambda-rie

COPY handler.py .

CMD ["handler.lambda_handler"]
