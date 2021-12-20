FROM python:3.9.9-slim

# set env variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH /app/api


# install dependencies
COPY requirements.txt /app/
# set work directory
WORKDIR /app
RUN python -m pip install -r requirements.txt

# copy project
COPY api/ .

# EXPOSE 8000

# CMD [ "python", "-u", "-m", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--proxy-headers", "--port", "8000"]
