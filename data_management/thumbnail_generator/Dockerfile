FROM public.ecr.aws/lambda/python:3.13

COPY thumbnail_generator/ ${LAMBDA_TASK_ROOT}/

RUN pip install --no-cache-dir -r ${LAMBDA_TASK_ROOT}/requirements.txt

CMD ["main.lambda_handler"]
