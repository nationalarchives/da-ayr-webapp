FROM public.ecr.aws/lambda/python:3.12

ARG DROID_VERSION=6.9.13

# Install Java for DROID, plus unzip to unpack the downloaded release
RUN dnf install -y java-21-amazon-corretto-headless unzip && dnf clean all

# Download and unpack the DROID binary distribution from GitHub releases
# (replaces COPY droid/ /opt/droid/ — DROID is no longer vendored in the repo)
RUN mkdir -p /opt/droid && \
    curl -fL -o /tmp/droid.zip \
      "https://github.com/digital-preservation/droid/releases/download/${DROID_VERSION}/droid-binary-${DROID_VERSION}-bin.zip" && \
    unzip -q /tmp/droid.zip -d /opt/droid && \
    rm /tmp/droid.zip


RUN pip install --no-cache-dir --upgrade pip

RUN rm -f /usr/local/bin/aws-lambda-rie

# Copy Lambda handler
COPY handler.py ${LAMBDA_TASK_ROOT}/handler.py

RUN chmod +x /opt/droid/droid.sh

ENV DROID_COMMAND=/opt/droid/droid.sh
ENV DROID_VERSION=${DROID_VERSION}

CMD ["handler.lambda_handler"]
