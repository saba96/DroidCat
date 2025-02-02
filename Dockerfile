FROM ubuntu:16.04

RUN apt update && apt upgrade -y

RUN apt install -y python python-pip openjdk-8-jdk

RUN pip install scikit-learn==0.18.1

RUN apt-get install git

RUN apt-get install -y zipalign
