FROM public.ecr.aws/lambda/python:3.12

WORKDIR ${LAMBDA_TASK_ROOT}

COPY handler.py .


CMD ["handler.lambda_handler"]
