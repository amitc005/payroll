
FROM python:3.6.9-slim-stretch
LABEL maintainer="Amit Chavhan <amitc005@gmail.com>"

RUN apt-get update && apt-get install -y vim

RUN mkdir /usr/local/payroll/
WORKDIR /usr/local/payroll/

COPY requirements.txt /usr/local/payroll/

RUN pip install -r requirements.txt
