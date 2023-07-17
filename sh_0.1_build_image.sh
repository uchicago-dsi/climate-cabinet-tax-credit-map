#Build the image
docker build -t py-docker-climate-cabinet .
#Run the image
docker run -it py-docker-climate-cabinet
#Run the image with a volume
# docker run -v /path/to/data:/app/data py-docker-climate-cabinet