# Pull official Python base image
FROM python:3.9

# Configure Python logs to stream to stdout without buffering
ENV PYTHONUNBUFFERED 1

# Install GDAL and related dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends gdal-bin libgdal-dev python3-gdal

# Set working directory in container
WORKDIR /pipeline

# Install requirements based on declared environment
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy remaining application code to container
COPY . .

# Run the development server
# TODO: trying to track down error in production cloud run
# CMD ["bash", "setup.sh", "--migrate", "--load-geos", "--load-programs", "--load-geo-metrics"]
CMD ["bash", "setup.sh", "--migrate", "--load-geos", "--load-programs"]
