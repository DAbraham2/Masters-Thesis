FROM python:3.12-alpine3.18
LABEL authors="daabraha"

RUN apk update \
    && apk add openjdk17-jdk openjdk17-jre linux-headers musl-dev gcc python3-dev\
    && apk cache clean


WORKDIR /graphwalker
COPY graphwalker-cli-4.3.2.jar ./
RUN echo '#!/bin/bash \
    java -jar /graphwalker/graphwalker-cli-4.3.2.jar "$@"' > gw.sh;

RUN chmod +x gw.sh

ENV PATH /graphwalker:$PATH

WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt \
    && pip cache purge


COPY application ./application
COPY combined_test_suite ./combined_test_suite
COPY gst_utils ./gst_utils
COPY interface ./interface
COPY models/mp-model.json ./models/
COPY plugins ./plugins
COPY scenario ./scenario
COPY transport ./transport
COPY main.py .

ENV PYTHONPATH /app:$PYTHONPATH

ENTRYPOINT ["python", "./main.py"]