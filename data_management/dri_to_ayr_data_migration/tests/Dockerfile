FROM python:3.14-slim

ARG DROID_VERSION=6.9.13

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
org.bouncycastle:bcprov-jdk15on:1.79:bcprov-jdk18on \
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

ENV DROID_COMMAND=/opt/droid/droid.sh \
    DROID_VERSION=${DROID_VERSION} \
    DROID_TIMEOUT_SECONDS=120

WORKDIR /app


RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        openjdk-21-jre-headless \
        unzip && \
    rm -rf /var/lib/apt/lists/*

# Download and unpack DROID.
RUN mkdir -p /opt/droid && \
    curl -fsSL -o /tmp/droid.zip \
      "https://github.com/digital-preservation/droid/releases/download/${DROID_VERSION}/droid-binary-${DROID_VERSION}-bin.zip" && \
    unzip -q /tmp/droid.zip -d /opt/droid && \
    chmod +x /opt/droid/droid.sh && \
    rm -f /tmp/droid.zip


RUN set -eu; \
    for entry in $DROID_JAR_PATCHES; do \
      group_id=$(echo "$entry" | cut -d: -f1); \
      artifact_id=$(echo "$entry" | cut -d: -f2); \
      new_version=$(echo "$entry" | cut -d: -f3); \
      replacement_artifact=$(echo "$entry" | cut -d: -f4); \
      if [ -z "$replacement_artifact" ]; then \
        replacement_artifact="$artifact_id"; \
      fi; \
      group_path=$(echo "$group_id" | tr '.' '/'); \
      existing_jar=$(find /opt/droid/lib \
        -maxdepth 1 \
        -type f \
        -name "${artifact_id}-[0-9]*.jar" \
        -print \
        -quit); \
      if [ -z "$existing_jar" ]; then \
        echo "Could not find existing DROID JAR for ${artifact_id}" >&2; \
        exit 1; \
      fi; \
      original_name=$(basename "$existing_jar"); \
      patched_jar="/opt/droid/lib/${replacement_artifact}-${new_version}.jar"; \
      if [ "$existing_jar" = "$patched_jar" ]; then \
        echo "JAR already patched before this step: ${existing_jar}" >&2; \
        exit 1; \
      fi; \
      echo "Replacing ${original_name} with $(basename "$patched_jar")"; \
      curl -fsSL -o "$patched_jar" \
        "https://repo1.maven.org/maven2/${group_path}/${replacement_artifact}/${new_version}/${replacement_artifact}-${new_version}.jar"; \
      rm -f "$existing_jar"; \
      ln -s "$(basename "$patched_jar")" \
        "/opt/droid/lib/$original_name"; \
    done

# Fail the build if Java or DROID cannot start.
RUN test -x "${DROID_COMMAND}" && \
    java -version && \
    "${DROID_COMMAND}" --help >/dev/null

RUN pip install --no-cache-dir --upgrade pip
