import os
import scripts.preprocess_helper as ph
import scripts.cleanup_helper as ch
import scripts.overlay_map_helper as omh
import omegaconf

def load_data(paths: dict) -> dict:
    """
    Load data from various file paths specified in the 'paths' dictionary.

    Parameters:
        paths (dict): A dictionary containing file paths for different datasets.

    Returns:
        dict: A dictionary containing the loaded data, where keys represent the dataset names
              and values are the corresponding data loaded from the specified file paths.
    """
    data = {}
    datasets = {'utils_raw': paths.utilities.util_shape_file_path,'j40_raw': paths.j40.j40_shp_path,'coal_raw': paths.energy.coal_shp_path,
                'ffe_raw': paths.energy.ffe_shp_path,'states_fips': paths.boundaries.state_fips_path,'ct_raw': paths.boundaries.ct_path,
                'st_raw': paths.boundaries.st_path,'dci_raw': paths.dci.dci_csv_path,'zip_shp': paths.dci.zip_shp_path}

    for name, file_path in datasets.items():
        file_type = 'shp' if file_path.endswith('.shp') else 'csv'
        data[name] = ph.load_data(file_path, file_type)

    return data

def data_clean(utils_raw, j40_raw, coal_raw, ffe_raw, states_fips, ct_raw, st_raw, dci_raw, zip_shp, lic_paths, consts):
    """
    Perform data cleaning on the raw datasets.

    Parameters:
        utils_raw (geopandas.GeoDataFrame): Raw utility shapefile data.
        j40_raw (geopandas.GeoDataFrame): Raw J40 shapefile data.
        coal_raw (geopandas.GeoDataFrame): Raw coal shapefile data.
        ffe_raw (geopandas.GeoDataFrame): Raw FFE shapefile data.
        states_fips (pandas.DataFrame): Dataframe containing state FIPS codes.
        ct_raw (geopandas.GeoDataFrame): Raw county shapefile data.
        st_raw (geopandas.GeoDataFrame): Raw state shapefile data.
        dci_raw (pandas.DataFrame): Raw DCI CSV data.
        zip_shp (geopandas.GeoDataFrame): Raw ZIP code shapefile data.
        lic_paths (namedtuple): Namedtuple containing paths to low-income related datasets.
        consts (OmegaConf): Configuration constants.

    Returns:
        tuple: A tuple containing cleaned dataframes and geodataframes for various datasets:
               (util_clean, rural_coops, municipal_utils, j40_clean, coal_clean, ffe_clean,
               lic_clean, county_df, state_df, dci_clean).
    """
    util_clean, rural_coops, municipal_utils = ch.coops_utils_cleanup(util_shp=utils_raw, state_csv_df=states_fips, consts=consts.utilities)
    j40_clean = ch.j40_cleanup(j40_shp=j40_raw.copy(), consts=consts.j40)
    coal_clean, ffe_clean = ch.energy_cleanup(coal_shp=coal_raw.copy(), ffe_shp=ffe_raw.copy(), consts=consts.energy)
    lic_clean = ch.low_inc_cleanup(pov_csv_path=lic_paths.pov_dir, li_tract_csv_path=lic_paths.tract_inc_dir,
                                   li_st_csv_path=lic_paths.st_inc_dir, li_msa_csv_path=lic_paths.msa_inc_dir,
                                   tracts_shp_path=lic_paths.tract_shp_path, msa_shp_path=lic_paths.msa_shape_path,
                                   consts=consts.low_income)
    county_df, state_df = ch.cty_st_borders_cleanup(county_df=ct_raw.copy(), st_fips_csv=states_fips, st_df=st_raw.copy(),
                                                   consts=consts.ct_st_borders)
    dci_clean = ch.dci_cleanup(dci_csv_df=dci_raw.copy(), zip_shp=zip_shp.copy(), consts=consts.dci)

    return util_clean, rural_coops, municipal_utils, j40_clean, coal_clean, ffe_clean, lic_clean, county_df, state_df, dci_clean

def generate_overlays(community_list, rural_coops, municipal_utils, community_data_list, consts):
    """
    Generate overlays for different communities using utility and other data.

    Parameters:
        community_list (list): List of community names.
        rural_coops (geopandas.GeoDataFrame): Cleaned data for rural cooperatives utilities.
        municipal_utils (geopandas.GeoDataFrame): Cleaned data for municipal utilities.
        community_data_list (list): List of cleaned data corresponding to each community.
        consts (OmegaConf): Configuration constants.

    Returns:
        dict: A dictionary containing the generated overlays, where keys are the overlay names
              and values are the corresponding overlay data.
    """
    overlays = {}
    for i, community in enumerate(community_list):
        community_data = community_data_list[i]
        overlays[community + '_coop'] = omh.overlays(community=community, coops_utils=rural_coops, community_data=community_data, consts=consts)
        overlays[community + '_muni'] = omh.overlays(community=community, coops_utils=municipal_utils, community_data=community_data, consts= consts)
    return overlays

def generate_and_save_map(utilities,overlays, county_df, state_df, type, consts, state, save_path):
    """
    Generate and save the overlay map for a specific state and community type.

    Parameters:
        utilities (geopandas.GeoDataFrame): Cleaned data for utilities (either rural cooperatives or municipal utilities).
        overlays (dict): A dictionary containing the generated overlays for the community type.
        county_df (geopandas.GeoDataFrame): Cleaned data for county borders.
        state_df (geopandas.GeoDataFrame): Cleaned data for state borders.
        type (str): Type of community ('coops' for rural cooperatives or 'muni' for municipal utilities).
        consts (OmegaConf): Configuration constants.
        state (str): Name of the state for which the overlay map is generated.
        save_path (str): Path to save the generated overlay map HTML file.

    Returns:
        None
    """
    try:
        map = omh.create_overlay_map(coops_utils=utilities, overlays=overlays, cty_borders=county_df, state_borders=state_df, type=type, consts=consts, state=state)
        save_path = os.path.join(os.getcwd(),save_path, state + '_overlay.html').replace('\\','/')
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        map.save(save_path)
        return None
    except Exception as e:
        raise e


def main() -> None:
    wd = os.getcwd().replace('\\', '/')
    os.chdir(wd)
    yaml_path = os.path.join(wd, 'conf', 'config.yaml')
    cfg = omegaconf.OmegaConf.load(yaml_path)
    consts = cfg.constants
    paths = cfg.paths
    #Read and clean the data
    utils_raw, j40_raw, coal_raw, ffe_raw, states_fips, ct_raw, st_raw, dci_raw, zip_shp = load_data(paths).values() 
    res_data_clean = data_clean(utils_raw, j40_raw, coal_raw, ffe_raw, states_fips, ct_raw, st_raw, dci_raw, zip_shp, paths.low_income, consts)
    util_clean, rural_coops, municipal_utils, j40_clean, coal_clean, ffe_clean, lic_clean, county_df, state_df, dci_clean = res_data_clean
    lic_clean = lic_clean[lic_clean['Type']=='Low Income']
    #Generate the overlays
    community_list = ['j40', 'coal', 'ffe', 'low_income', 'dci']
    overlays = generate_overlays(community_list, rural_coops, municipal_utils, [j40_clean, coal_clean, ffe_clean, lic_clean, dci_clean], consts.overlays)
    #Create the maps and save it
    coop_overlays = {'j40': overlays['j40_coop'],'coal': overlays['coal_coop'],'ffe': overlays['ffe_coop'],
                    'lic': overlays['low_income_coop'],'dci': overlays['dci_coop']}
    mun_overlays = {'j40': overlays['j40_muni'],'coal': overlays['coal_muni'],'ffe': overlays['ffe_muni'],
                    'lic': overlays['low_income_muni'],'dci': overlays['dci_muni']}
    generate_and_save_map(rural_coops,coop_overlays, county_df, state_df, 'coops', consts.maps, 'Illinois',paths.maps.coops_html_path)
    generate_and_save_map(municipal_utils,mun_overlays, county_df, state_df, 'municipal',consts.maps, 'Illinois', paths.maps.utils_html_path)


if __name__ == '__main__':
    main()