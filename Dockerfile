#Use python 3.9 as the base image
FROM python:3.9-slim

#Set the working directory to /scripts
WORKDIR /app

#Copy the scripts directory contents into the container at /scripts, and then the requirements.txt file
COPY ./scripts ./scripts
COPY ./requirements.txt ./requirements.txt
COPY ./conf ./conf

#Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org --no-cache-dir -r requirements.txt

#Make a results directory within the container to store the results
RUN mkdir /app/results

#Run the main.py script when the container launches
CMD ["python", "./main.py"]