#Use python 3.9 as the base image
FROM --platform=linux/amd64 osgeo/gdal:ubuntu-full-3.6.3

RUN apt-get -y update 

RUN apt -y install python3-pip libspatialindex-dev \
    && apt-get install -y --no-install-recommends \
       gdal-bin \
       libgdal-dev \
    && rm -rf /var/lib/apt/lists/*

#Set the working directory to /scripts
WORKDIR /app

#Install any needed packages specified in requirements.txt
COPY ./requirements.txt requirements.txt
RUN pip install --trusted-host pypi.python.org --no-cache-dir -r requirements.txt

#Copy the scripts directory contents into the container at /scripts, and then the requirements.txt file
COPY ./scripts ./scripts
COPY ./conf ./conf
COPY main.py .

#Make a results directory within the container to store the results
RUN mkdir /app/results

#Run the main.py script when the container launches
CMD ["python", "main.py"]