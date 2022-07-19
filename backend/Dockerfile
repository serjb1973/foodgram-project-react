FROM python:3.7-slim
RUN apt-get update && apt-get -y install libpq-dev gcc
WORKDIR /app
COPY ./foodgram/ .
COPY requirements.txt .
RUN pip install --upgrade pip --upgrade setuptools
RUN pip install -r ./requirements.txt --no-cache-dir
CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0:8000"]
