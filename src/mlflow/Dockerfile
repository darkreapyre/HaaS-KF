FROM python:3.7.0

ARG BUCKET
ENV bucket=$BUCKET

RUN mkdir /mlflow/
RUN pip install --upgrade pip
RUN pip --no-cache-dir install mlflow awscli

EXPOSE 5000

CMD mlflow server --default-artifact-root s3://${bucket}/mlflow-artifacts --host 0.0.0.0