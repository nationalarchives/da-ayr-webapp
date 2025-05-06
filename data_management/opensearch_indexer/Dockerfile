FROM python:3.13.2

RUN apt-get update && apt-get install -y \
    python-dev-is-python3 \
    libxml2-dev libxslt1-dev \
    antiword unrtf poppler-utils tesseract-ocr \
    flac ffmpeg lame libmad0 libsox-fmt-mp3 sox \
    libjpeg-dev swig \
    # postgresql-contrib


COPY requirements.txt ${LAMBDA_TASK_ROOT}

# Install the function's dependencies
RUN pip install \
        awslambdaric \
        -r requirements.txt

COPY opensearch_indexer/ ${LAMBDA_TASK_ROOT}/opensearch_indexer

# Set runtime interface client as default command for the container runtime
ENTRYPOINT [ "/usr/local/bin/python", "-m", "awslambdaric" ]

# Pass the name of the function handler as an argument to the runtime
CMD [ "opensearch_indexer.index_consignment.lambda_function.lambda_handler" ]
