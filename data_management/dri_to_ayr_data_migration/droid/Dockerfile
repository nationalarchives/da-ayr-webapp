FROM public.ecr.aws/lambda/python:3.12

ARG DROID_VERSION=6.9.13

# Pinned patched versions for CVEs in DROID's bundled dependencies, sourced
# from the full Wiz/ECR scan export (not partial terminal output — get a
# full CSV/JSON export each time this needs re-checking, since DROID's
# lib/ folder has ~40 jars and partial scan snippets miss things).
# DROID's own release doesn't refresh these on its own schedule, so we
# override the vulnerable jars after unpacking. Re-check against each
# scan and against any future DROID_VERSION bump.
#
# Format: "mavenGroupId:artifactId:newVersion". Versions are the final
# target the pristine 6.9.13 zip needs to reach (not intermediate
# versions from a previously-patched image's scan).
ARG DROID_JAR_PATCHES="\
io.netty:netty-codec:4.1.136.Final \
io.netty:netty-codec-http:4.1.137.Final \
io.netty:netty-codec-http2:4.1.136.Final \
org.apache.httpcomponents.core5:httpcore5:5.4.3 \
org.apache.httpcomponents.core5:httpcore5-h2:5.4.3 \
org.apache.httpcomponents.client5:httpclient5:5.6.3 \
org.apache.logging.log4j:log4j-api:2.26.1 \
com.fasterxml.jackson.core:jackson-databind:2.22.1 \
org.bouncycastle:bcprov-jdk15to18:1.84 \
org.bouncycastle:bcprov-jdk15on:1.79 \
org.eclipse.angus:angus-mail:2.0.4 \
org.apache.cxf:cxf-core:4.2.3 \
org.apache.cxf:cxf-rt-bindings-soap:4.2.3 \
org.apache.cxf:cxf-rt-bindings-xml:4.2.3 \
org.apache.cxf:cxf-rt-databinding-jaxb:4.2.3 \
org.apache.cxf:cxf-rt-frontend-jaxws:4.2.3 \
org.apache.cxf:cxf-rt-frontend-simple:4.2.3 \
org.apache.cxf:cxf-rt-transports-http:4.2.3 \
org.apache.cxf:cxf-rt-ws-addr:4.2.3 \
org.apache.cxf:cxf-rt-ws-policy:4.2.3 \
"

# Install Java for DROID, plus unzip to unpack the downloaded release
RUN dnf install -y java-21-amazon-corretto-headless unzip && dnf clean all

# Download and unpack the DROID binary distribution from GitHub releases
# (replaces COPY droid/ /opt/droid/ — DROID is no longer vendored in the repo)
RUN mkdir -p /opt/droid && \
    curl -fL -o /tmp/droid.zip \
      "https://github.com/digital-preservation/droid/releases/download/${DROID_VERSION}/droid-binary-${DROID_VERSION}-bin.zip" && \
    unzip -q /tmp/droid.zip -d /opt/droid && \
    rm /tmp/droid.zip

# Patch vulnerable dependencies bundled inside DROID's lib/ folder.
# The glob anchors on "artifactId-<digit>" so overlapping names
# (netty-codec / netty-codec-http / netty-codec-http2,
#  httpcore5 / httpcore5-h2) can't cross-match each other.
RUN for entry in $DROID_JAR_PATCHES; do \
      group_id=$(echo "$entry" | cut -d: -f1); \
      artifact_id=$(echo "$entry" | cut -d: -f2); \
      new_version=$(echo "$entry" | cut -d: -f3); \
      group_path=$(echo "$group_id" | tr '.' '/'); \
      rm -f /opt/droid/lib/${artifact_id}-[0-9]*.jar && \
      curl -fL -o /opt/droid/lib/${artifact_id}-${new_version}.jar \
        "https://repo1.maven.org/maven2/${group_path}/${artifact_id}/${new_version}/${artifact_id}-${new_version}.jar"; \
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
