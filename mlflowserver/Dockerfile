FROM continuumio/miniconda3

ARG DEBIAN_FRONTEND="noninteractive"
RUN apt-get update && \
    apt-get install -y default-libmysqlclient-dev build-essential && \
    apt-get clean && \
    rm -rf /var/cache/apt/archives/* /var/lib/apt/lists/*

RUN pip install 'protobuf>=3.20.0,<4' 'mlflow>=1.24.0,<1.25' mysqlclient sqlalchemy boto3
RUN mkdir -p /mlflow
WORKDIR /mlflow

RUN groupadd -r mlflow_server && useradd --no-log-init -r -g mlflow_server mlflow_server
USER mlflow_server
