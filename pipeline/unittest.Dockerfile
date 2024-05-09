FROM python:3.11
ENV PYTHONUNBUFFERED 1
RUN apt-get update && \
    apt-get install -y --no-install-recommends gdal-bin libgdal-dev python3-gdal && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
WORKDIR /pipeline
COPY requirements.txt requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements.txt -r requirements-dev.txt
COPY . .