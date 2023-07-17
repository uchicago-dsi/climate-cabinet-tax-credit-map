# climate-cabinet-tax-credit-map

This repository contains code to create the interactive maps to help understand the public utilities' eligibility for clean energy tax credit bonuseses.  The idea is to highlight the areas on a folium map that are occupied by the disadvantaged communities as per the IRA and map them on top of the area covered by the Rural Cooperatives or Municipal Utilities which could serve as a tool for Climate Cabinet to refer. 


## Code Structure

The repository has the following structure:

- `main.py`: The main Python file used to run the scripts.
- `scripts`: A directory containing the python scripts needed to:
    - Data load/scrape, 
    - Data cleanup, 
    - Feature engineering, 
    - Generate dataset overlays, and 
    - Produces interactive folium maps.
- `requirements.txt`: Contains Python packages required to run the scripts and can be used for creating a custom Docker container image for training.
- `Dockerfile`: Contains instructions for building the custom training Docker container image.
- `sh_0.1_build_image.sh`: Shell script to build the custom training container image.


## Usage

To run the scripts locally, follow these steps:

1. **Clone the repository**.
2. **Create a virtual Python environment:** You should create a virtual Python environment to run the code in this repository. Follow the instructions [here](https://virtualenv.pypa.io/en/stable/user_guide.html) to create a virtual environment using `virtualenv`. Can use the below command if using anaconda:
```bash
conda create -n myenv
```
3. **Activate the virtual environment:** Activate the virtual environment you created in Step 2.
```bash
source /path/to/venv/bin/activate
```
If using anaconda:
```bash
conda activate myenv
```
4. **Install the required packages in your activated virtual environment:** 
```bash
pip install -r requirements.txt
```
<!-- 5. **Select your virtual environment as your kernel in the Jupyter Notebook :** You can use [ipykernel](https://janakiev.com/blog/jupyter-virtual-envs/) to add the virtual environment to your notebook. -->

5. **Download the data:** Download from this [GDrive URL](https://drive.google.com/drive/u/1/folders/1RSVQ8qlabg9ZNqzHjma82X_w4CKoWia8) and save it in `data` folder in the root directory of the project.

Once all the steps above are complete, you should be able to run the main file (`main.py`). When the file has finished running, an HTML file will be saved in the `results` directory and can be opened from a browser to check the output map.


To run the scripts using a docker container:
- Have both the `Dockerfile` and the `sh_0.1_build_image.sh` script in the root directory and run the shell script using terminal command:
    - Check for the storage mounting command from the script before exucuting it.
```bash
sh sh_0.1_build_image.sh
```


## Further Reading

More detailed information about what each script does is documented in the `README.md` file within the scripts directory.