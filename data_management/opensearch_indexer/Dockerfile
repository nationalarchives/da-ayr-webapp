FROM public.ecr.aws/lambda/python:3.11
# use python 3.11, not 3.12 due to issues with textract on 3.12 at the moment

RUN yum install -y python-dev libxml2-dev libxslt1-dev antiword unrtf poppler-utils pstotext tesseract-ocr \
flac ffmpeg lame libmad0 libsox-fmt-mp3 sox libjpeg-dev swig

COPY requirements.txt ${LAMBDA_TASK_ROOT}

RUN pip install -r requirements.txt

COPY opensearch_indexer/ ${LAMBDA_TASK_ROOT}/opensearch_indexer

CMD [ "opensearch_indexer.lambda_function.lambda_handler" ]
