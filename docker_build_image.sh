#Build the image
docker build -t py-docker-climate-cabinet .
#Run the image with a volume
docker run -v ./data:/app/data py-docker-climate-cabinet