##Make a docker file to build the image to run all the scripts from the scripts folder
#Use python 3.9 as the base image
FROM python:3.9

#Set the working directory to /scripts
WORKDIR /app

#Copy the scripts directory contents into the container at /scripts, and then the requirements.txt file
COPY ./scripts ./scripts
COPY ./requirements.txt ./requirements.txt

#Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt

#Run the main.py script when the container launches
CMD ["python", "./main.py"]

#Build the image
#docker build -t py-docker-climate-cabinet .
#Run the image
#docker run -it py-docker-climate-cabinet
#Run the image with a volume
#docker run -v /path/to/data:/app/data py-docker-climate-cabinet