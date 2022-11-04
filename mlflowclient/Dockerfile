FROM python:3.10.8-slim-bullseye as base
ENV PYTHONUNBUFFERED=1

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

WORKDIR /mlflow_client


RUN apt-get update && \
    apt-get install -y default-libmysqlclient-dev build-essential && \
    apt-get clean && \
    rm -rf /var/cache/apt/archives/* /var/lib/apt/lists/*

RUN pip install 'protobuf>=3.20.0,<4' 'mlflow>=1.24.0,<1.25' mysqlclient sqlalchemy boto3

RUN groupadd -r mlflow_client && useradd --no-log-init -r -g mlflow_client mlflow_client
USER mlflow_client

