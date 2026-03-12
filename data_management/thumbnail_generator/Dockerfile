# Python 3.13-slim — same base as access_copy_converter for consistency
FROM python@sha256:151ab3571dad616bb031052e86411e2165295c7f67ef27206852203e854bcd12

COPY thumbnail_generator/ /app/

RUN pip install --no-cache-dir -r /app/requirements.txt

WORKDIR /app

# ECS entry point.  The same image can be deployed as a Lambda container
# image by overriding CMD to point at the Lambda handler:
#   CMD ["main.lambda_handler"]
CMD ["python", "main.py"]
