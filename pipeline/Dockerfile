# Pull official Python base image
FROM python:3.11

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
CMD ["bash", "setup.sh", "--migrate", "--load-base-tables", "--load-dependent-tables", "--load-assoc-table"]
# CMD ["bash", "setup.sh", "--migrate", "--load-assoc-table"]

    # "--load-base-tables", 
    # "--load-dependent-tables"]
# , "--load-assoc-table"]
