FROM python:3.9-alpine

ENV PYTHONUNBUFFERED 1

# Install postgres client
RUN apk add --update --no-cache postgresql-client

# Install individual dependencies
# so that we could avoid installing extra packages to the container
RUN apk add --update --no-cache --virtual .tmp-build-deps \
    gcc libc-dev linux-headers postgresql-dev libffi-dev

RUN apk update && apk add libpq alpine-sdk jpeg-dev zlib-dev libjpeg

COPY . /app
WORKDIR /app
RUN mkdir staticfiles

RUN pip install --upgrade pip && python -m pip install uvicorn[standard] && pip install -r requirements.txt

# Remove dependencies
RUN apk del .tmp-build-deps

# [Security] Limit the scope of user who run the docker image
