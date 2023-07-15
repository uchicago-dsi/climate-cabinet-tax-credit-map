import subprocess

def main():
    '''
    Runs the scripts in the scripts folder in the order they need to be run.
    '''
    subprocess.run(["python", "./scripts/coop_utility_cleanup.py"])
    subprocess.run(["python", "./scripts/county_st_borders.py"])
    subprocess.run(["python", "./scripts/tract_file_scraper.py"])
    subprocess.run(["python", "./scripts/justice40_cleanup.py"])
    subprocess.run(["python", "./scripts/energy_comm_cleanup.py"])
    subprocess.run(["python", "./scripts/low_inc_cleanup.py"])
    subprocess.run(["python", "./scripts/overlays.py"])
    subprocess.run(["python", "./scripts/maps.py"])

if __name__ == "__main__":
    main()