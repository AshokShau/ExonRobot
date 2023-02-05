FROM debian:11
FROM python:3.10.5-slim-buster

WORKDIR /Exon/

RUN apt-get update && apt-get upgrade -y
RUN apt-get -y install git
RUN python3 -m pip install -U pip
RUN apt-get install -y wget python3-pip curl bash neofetch ffmpeg software-properties-common

COPY requirements.txt .

RUN pip3 install wheel
RUN pip3 install -U -r requirements.txt

COPY . .
CMD bash start
