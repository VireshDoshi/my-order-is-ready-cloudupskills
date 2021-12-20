FROM python:3.9.9-slim

# set work directory
WORKDIR /app/dashboard

# set env variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST 0.0.0.0

# install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# copy project
COPY dashboard/ .