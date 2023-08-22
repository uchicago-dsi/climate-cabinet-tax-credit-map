import os
import scripts.preprocess_helper as ph
import scripts.cleanup_helper as ch
import scripts.overlay_map_helper as omh
from tobler.area_weighted import area_interpolate
import pandas as pd
import geopandas as gpd


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
    datasets = {
        "utils_raw": paths.utilities.util_shape_file_path,
        "j40_raw": paths.j40.j40_shp_path,
        "coal_raw": paths.energy.coal_shp_path,
        "ffe_raw": paths.energy.ffe_shp_path,
        "states_fips": paths.boundaries.state_fips_path,
        "ct_raw": paths.boundaries.ct_path,
        "st_raw": paths.boundaries.st_path,
        "dci_raw": paths.dci.dci_csv_path,
        "zip_shp": paths.dci.zip_shp_path,
    }

    for name, file_path in datasets.items():
        file_type = "shp" if file_path.endswith(".shp") else "csv"
        data[name] = ph.load_data(file_path, file_type)

    return data


def data_clean(
    utils_raw,
    j40_raw,
    coal_raw,
    ffe_raw,
    states_fips,
    ct_raw,
    st_raw,
    dci_raw,
    zip_shp,
    lic_paths,
    consts,
):
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
    util_clean, rural_coops, municipal_utils = ch.coops_utils_cleanup(
        util_shp=utils_raw, state_csv_df=states_fips, consts=consts.utilities
    )
    j40_clean = ch.j40_cleanup(j40_shp=j40_raw.copy(), consts=consts.j40)
    coal_clean, ffe_clean = ch.energy_cleanup(
        coal_shp=coal_raw.copy(), ffe_shp=ffe_raw.copy(), consts=consts.energy
    )
    lic_clean = ch.low_inc_cleanup(
        pov_csv_path=lic_paths.pov_dir,
        li_tract_csv_path=lic_paths.tract_inc_dir,
        li_st_csv_path=lic_paths.st_inc_dir,
        li_msa_csv_path=lic_paths.msa_inc_dir,
        tracts_shp_path=lic_paths.tract_shp_path,
        msa_shp_path=lic_paths.msa_shape_path,
        consts=consts.low_income,
    )
    county_df, state_df = ch.cty_st_borders_cleanup(
        county_df=ct_raw.copy(),
        st_fips_csv=states_fips,
        st_df=st_raw.copy(),
        consts=consts.ct_st_borders,
    )
    dci_clean = ch.dci_cleanup(
        dci_csv_df=dci_raw.copy(), zip_shp=zip_shp.copy(), consts=consts.dci
    )

    return (
        util_clean,
        rural_coops,
        municipal_utils,
        j40_clean,
        coal_clean,
        ffe_clean,
        lic_clean,
        county_df,
        state_df,
        dci_clean,
    )


class PopulationProcessor:
    def __init__(self, consts, paths):
        self.consts = consts
        self.paths = paths

    def load_pop_data(self):
        """
        Load population data from various file paths specified in the 'paths' dictionary.

        Parameters:
            consts (dict): A dictionary containing file names for different population datasets.
            paths (dict): A dictionary containing file paths for different population datasets.

        Returns:
            dict: A dictionary containing the loaded population data, where keys represent the dataset names
        """
        pop_files = self.consts
        data = {}
        for key, file_type in pop_files.items():
            file_path = getattr(self.paths, f"{key}_path")
            data[key] = ph.load_data(file_path, file_type)
        return data

    def pop_clean(self, data, geo_types):
        """
        Clean and merge population data for specified geography types.

        This function processes population data for the specified geography types (tract, msa, county)
        by cleaning the data, merging it with corresponding shapefiles, and saving the merged data
        as shapefiles in the specified output paths.

        Args:
            data (dict): A dictionary containing the raw population data for each geography type.
            geo_types (list): A list of geography types to process (e.g., ['tract', 'msa', 'county']).
            consts (dict): A dictionary containing constants and configuration for data cleaning and merging.
            paths (dict): A dictionary containing file paths for saving the cleaned and merged data.

        Returns:
            dict: A dictionary containing the merged data for each geography type, with keys as the geography
            type names and values as the corresponding merged GeoDataFrames.

        Raises:
            AssertionError: If the number of merged GeoDataFrames in the output dictionary is not equal to the
            number of geography types specified.
        """
        pop_cleaner = ch.PopulationCleanup(consts=self.consts)
        merged_data_dict = {}

        for geo_type in geo_types:
            clean_df = pop_cleaner._clean_csv_data(data[geo_type], geo_type)
            merged_df = pop_cleaner.merge_data_with_shapefile(
                clean_df, data[geo_type + "_shp"], geo_type
            )

            save_path = self.paths[geo_type + "_pop_shp"]
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            ph.save_data(merged_df, save_path, "shp")

            merged_data_dict[geo_type] = merged_df
        assert len(merged_data_dict) == 3
        return merged_data_dict.items()


def generate_overlays(
    community_list,
    rural_coops,
    municipal_utils,
    community_data_list,
    consts,
    paths=None,
):
    """
    Generate overlays for different communities using utility and other data, and also saves them as ESRI Shape files.

    Parameters:
        community_list (list): List of community names.
        rural_coops (geopandas.GeoDataFrame): Cleaned data for rural cooperatives utilities.
        municipal_utils (geopandas.GeoDataFrame): Cleaned data for municipal utilities.
        community_data_list (list): List of cleaned data corresponding to each community.
        consts (OmegaConf): Configuration constants.
        paths (dict): A dictionary containing file paths for saving the overlays.
    Returns:
        dict: A dictionary containing the generated overlays, where keys are the overlay names
              and values are the corresponding overlay data.
    """
    overlays = {}
    overlay_type_map = {"coop": rural_coops, "muni": municipal_utils}
    for i, community in enumerate(community_list):
        community_data = community_data_list[i]
        for overlay_type, coops_utils in overlay_type_map.items():
            overlay_key = community + "_" + overlay_type
            overlays[overlay_key] = omh.overlays(
                community=community,
                coops_utils=coops_utils,
                community_data=community_data,
                consts=consts.overlays,
            )

        if paths is not None:
            overlay_path = paths.overlays[overlay_type + "s"][
                community + "_overlay_path"
            ]
            os.makedirs(os.path.dirname(overlay_path), exist_ok=True)
            overlays[overlay_key].to_file(overlay_path, driver="ESRI Shapefile")
        else:
            raise ValueError("Output path for overlays is not specified.")

    return overlays


def generate_and_save_map(
    utilities, overlays, county_df, state_df, type, consts, state, save_path
):
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
        map = omh.create_overlay_map(
            coops_utils=utilities,
            overlays=overlays,
            cty_borders=county_df,
            state_borders=state_df,
            type=type,
            consts=consts,
            state=state,
        )
        save_path = os.path.join(
            os.getcwd(), save_path, state + "_overlay.html"
        ).replace("\\", "/")
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        map.save(save_path)
        return None
    except Exception as e:
        raise e


class InterpolationProcessor:
    """
    Class for interpolating population data for different communities."""

    def __init__(self, consts, paths):
        self.consts = consts
        self.paths = paths

    def interpolate_population(self, source_df, target_df):
        """
        Interpolate population data for a community using source and target dataframes.

        Parameters:
            source_df (geopandas.GeoDataFrame): Dataframe containing population data for the source geography type.
            target_df (geopandas.GeoDataFrame): Dataframe containing population data for the target geography type.

        Returns:
            geopandas.GeoDataFrame: Dataframe containing the interpolated population data for the target geography type.
        """
        results = area_interpolate(
            source_df=source_df,
            target_df=target_df,
            extensive_variables=[self.consts.interpolate.extensive],
        )
        overlay_df_with_pop = target_df.merge(
            results[self.consts.interpolate.merge_cols], on=self.consts.geo, how="left"
        )
        return overlay_df_with_pop

    def process_interpolation(self, overlays, data, save: bool = False):
        """
        Process interpolation for different communities using the specified data.

        Parameters:
            overlays (dict): A dictionary containing the generated overlays for different communities.
            data (dict): A dictionary containing the population data for different geography types.
            save (bool): Boolean flag to save the interpolated population data as shapefiles.

        Returns:
            dict: A dictionary containing the interpolated population data for different communities.
        """
        interpolated_results = {}

        for overlay_key in overlays.keys():
            if overlay_key.startswith(("j40", "coal", "lic", "dci")):
                interpolated_results[overlay_key] = self.interpolate_population(
                    data["tract_pop"], overlays[overlay_key]
                )
            elif overlay_key.startswith("ffe"):
                interpolated_results[overlay_key] = self.interpolate_population(
                    data["cty_pop"], overlays[overlay_key]
                )
        if save == True:
            for overlay_key, df in interpolated_results.items():
                output_path = self.paths[overlay_key + "_pop"]
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                ph.save_data(df, output_path, type="shp")
        return interpolated_results
