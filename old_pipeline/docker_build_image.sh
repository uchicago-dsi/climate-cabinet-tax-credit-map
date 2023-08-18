#!/bin/bash
set -e
#Build the image
docker build -t py-docker-climate-cabinet .
#Run the image with a volume
docker run -v $(pwd)/data:/app/data -v $(pwd)/results:/app/results py-docker-climate-cabinet
