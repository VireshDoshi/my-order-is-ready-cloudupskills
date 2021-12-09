FROM python:3.9.9

RUN apt-get -y update && apt-get -y install build-essential \
    libpulse-dev \
    swig \
    pulseaudio

# set work directory
WORKDIR /app

# set env variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# copy project
COPY speech/ .