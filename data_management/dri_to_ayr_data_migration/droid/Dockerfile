FROM public.ecr.aws/lambda/python:3.12

ARG DROID_VERSION=6.9.13

# Pinned patched versions for CVEs in DROID's bundled dependencies.
# DROID's own release doesn't refresh these on its own schedule, so we
# override the vulnerable jars after unpacking. Re-check filenames and
# versions against each scan and against any future DROID_VERSION bump.
ARG NETTY_CODEC_HTTP_VERSION=4.1.136.Final
ARG HTTPCORE5_H2_VERSION=5.4.3
ARG CXF_VERSION=4.2.3

# Install Java for DROID, plus unzip to unpack the downloaded release
RUN dnf install -y java-21-amazon-corretto-headless unzip && dnf clean all

# Download and unpack the DROID binary distribution from GitHub releases
# (replaces COPY droid/ /opt/droid/ — DROID is no longer vendored in the repo)
RUN mkdir -p /opt/droid && \
    curl -fL -o /tmp/droid.zip \
      "https://github.com/digital-preservation/droid/releases/download/${DROID_VERSION}/droid-binary-${DROID_VERSION}-bin.zip" && \
    unzip -q /tmp/droid.zip -d /opt/droid && \
    rm /tmp/droid.zip

# Patch vulnerable transitive dependencies bundled inside DROID's lib/ folder
# (confirmed via the 6.9.13 release zip: netty-codec-http-4.1.135.Final.jar,
# httpcore5-h2-5.4.jar, and 9 cxf-*-4.2.2.jar modules)
RUN rm -f /opt/droid/lib/netty-codec-http-*.jar && \
    curl -fL -o /opt/droid/lib/netty-codec-http-${NETTY_CODEC_HTTP_VERSION}.jar \
      "https://repo1.maven.org/maven2/io/netty/netty-codec-http/${NETTY_CODEC_HTTP_VERSION}/netty-codec-http-${NETTY_CODEC_HTTP_VERSION}.jar" && \
    rm -f /opt/droid/lib/httpcore5-h2-*.jar && \
    curl -fL -o /opt/droid/lib/httpcore5-h2-${HTTPCORE5_H2_VERSION}.jar \
      "https://repo1.maven.org/maven2/org/apache/httpcomponents/core5/httpcore5-h2/${HTTPCORE5_H2_VERSION}/httpcore5-h2-${HTTPCORE5_H2_VERSION}.jar" && \
    for module in core rt-bindings-soap rt-bindings-xml rt-databinding-jaxb \
                  rt-frontend-jaxws rt-frontend-simple rt-transports-http \
                  rt-ws-addr rt-ws-policy; do \
      rm -f /opt/droid/lib/cxf-${module}-*.jar && \
      curl -fL -o /opt/droid/lib/cxf-${module}-${CXF_VERSION}.jar \
        "https://repo1.maven.org/maven2/org/apache/cxf/cxf-${module}/${CXF_VERSION}/cxf-${module}-${CXF_VERSION}.jar"; \
    done

# Base image fixes: upgrade pip, drop aws-lambda-rie (local-testing-only
# binary, not used in real Lambda execution, so safe to remove for a
# deployed image)
RUN pip install --no-cache-dir --upgrade pip

RUN rm -f /usr/local/bin/aws-lambda-rie

# Copy Lambda handler
COPY handler.py ${LAMBDA_TASK_ROOT}/handler.py

RUN chmod +x /opt/droid/droid.sh

ENV DROID_COMMAND=/opt/droid/droid.sh
ENV DROID_VERSION=${DROID_VERSION}

CMD ["handler.lambda_handler"]
