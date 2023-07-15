##Make a docker file to build the image to run all the scripts from the scripts folder
#Use python 3.9 as the base image
FROM python:3.9

#Set the working directory to /scripts
WORKDIR /cc_temp

#Copy the scripts directory contents into the container at /scripts, and then the requirements.txt file
COPY scripts ./scripts
COPY requirements.txt /cc_temp/requirements.txt

#Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt

#Run the script when the container launches
# CMD ["python", "./scripts/coop_utility_cleanup.py"]
# CMD ["python", "./scripts/county_st_borders.py"]
# CMD ["python", "./scripts/tract_file_scraper.py"]
# CMD ["python", "./scripts/justice40_cleanup.py"]
# CMD ["python", "./scripts/energy_comm_cleanup.py"]
# CMD ["python", "./scripts/low_inc_cleanup.py"]
# CMD ["python", "./scripts/overlays.py"]
# CMD ["python", "./scripts/maps.py"]