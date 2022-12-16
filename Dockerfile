FROM python:3.10-slim-buster
EXPOSE 8000
RUN apt update && apt install iproute2 -y && apt install iputils-ping -y
WORKDIR /app
COPY ./requirements.txt /app
RUN pip install --upgrade pip && pip install -r requirements.txt --no-cache-dir
COPY . /app
ENTRYPOINT ["python3"]
CMD ["manage.py", "runserver", "0.0.0.0:8000"]
