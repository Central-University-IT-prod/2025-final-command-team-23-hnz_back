FROM python:3.11-alpine

RUN mkdir /code
WORKDIR /code
COPY . /code

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip
RUN pip install -r requirements.txt
