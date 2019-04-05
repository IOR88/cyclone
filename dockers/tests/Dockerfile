FROM ubuntu:latest
RUN apt-get update

RUN apt-get -y install python3-pip python3-dev build-essential

COPY . /home
RUN cd /home

RUN pip3 install -e .
RUN pip3 install pytest
RUN python src/cyclone/models.py
RUN pytest
RUN echo $?
