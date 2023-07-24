# climate-cabinet-tax-credit-map

This repository contains code to create the interactive maps to help understand the public utilities' eligibility for clean energy tax credit bonuseses.  The idea is to highlight the areas on a folium map that are occupied by the disadvantaged communities as per the IRA and map them on top of the area covered by the Rural Cooperatives or Municipal Utilities which could serve as a tool for Climate Cabinet to refer. 


## Code Structure

The repository has the following structure:

- `main.py`: The main Python file used to run the scripts.
- `scripts`: A directory with python scripts containing the helper functions needed to:
    - Data load/scrape, 
    - Data cleanup, 
    - Feature engineering, 
    - Generate dataset overlays, and 
    - Produces interactive folium maps.
- `requirements.txt`: Contains Python packages required to run the scripts and can be used for creating a custom Docker container image for training.
- `Dockerfile`: Contains instructions for building the custom training Docker container image.
- `docker_build_image.sh`: Shell script to build the custom training container image.

```bash
.git/
├──conf
├──notebooks
├──scripts
├──main.py
├──Dockerfile
└──requirements.txt
```

## Usage

To run the scripts locally, follow these steps:

1. **Clone the repository**.

2. **Download the data:** Download from this [GDrive URL](https://drive.google.com/drive/u/1/folders/1RSVQ8qlabg9ZNqzHjma82X_w4CKoWia8) and save it in `data` folder in the root directory of the project.

3. **Run the scripts using a docker container:**
- Have both the `Dockerfile` and the `docker_build_image.sh` script in the root directory and run the shell script using terminal command:
    - Check for the storage mounting command from the script before exucuting it.
```bash
sh docker_build_image.sh
```  
    - The container would run the `main.py` within itself and will produce the folium maps as HTML files in the results directory.

## Further Reading

More detailed information about what each script does is documented in the `README.md` file within the scripts directory.