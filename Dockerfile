FROM python:3.6-slim

ARG REQUIREMENT_PATH=requirements.txt

WORKDIR / 

RUN apt-get update -y

COPY requirements/ /requirements/

COPY requirements.txt requirements.txt

RUN pip install -r $REQUIREMENT_PATH 

VOLUME /src

COPY entrypoint.sh entrypoint.sh

RUN chmod +x entrypoint.sh

ENTRYPOINT /entrypoint.sh
