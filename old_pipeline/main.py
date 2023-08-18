import os
import scripts.main_helper as mh
import omegaconf

def main() -> None:
    wd = os.getcwd().replace('\\', '/')
    os.chdir(wd)
    yaml_path = os.path.join(wd, 'conf', 'config.yaml')
    cfg = omegaconf.OmegaConf.load(yaml_path)
    consts = cfg.constants
    paths = cfg.paths
    #Read and clean the data
    utils_raw, j40_raw, coal_raw, ffe_raw, states_fips, ct_raw, st_raw, dci_raw, zip_shp = mh.load_data(paths).values() 
    res_data_clean = mh.data_clean(utils_raw, j40_raw, coal_raw, ffe_raw, states_fips, ct_raw, st_raw, dci_raw, zip_shp, paths.low_income, consts)
    util_clean, rural_coops, municipal_utils, j40_clean, coal_clean, ffe_clean, lic_clean, county_df, state_df, dci_clean = res_data_clean
    lic_clean = lic_clean[lic_clean['Type']=='Low Income']
    #Generate the overlays
    community_list = ['j40', 'coal', 'ffe', 'lic', 'dci']
    overlays = mh.generate_overlays(community_list, rural_coops, municipal_utils, [j40_clean, coal_clean, ffe_clean, lic_clean, dci_clean], consts.overlays)
    #Create the maps and save them
    coop_overlays = {'j40': overlays['j40_coop'],'coal': overlays['coal_coop'],'ffe': overlays['ffe_coop'],
                    'lic': overlays['lic_coop'],'dci': overlays['dci_coop']}
    mun_overlays = {'j40': overlays['j40_muni'],'coal': overlays['coal_muni'],'ffe': overlays['ffe_muni'],
                    'lic': overlays['lic_muni'],'dci': overlays['dci_muni']}
    mh.generate_and_save_map(rural_coops,coop_overlays, county_df, state_df, 'coops', consts.maps, 'Illinois',paths.maps.coops_html_path)
    mh.generate_and_save_map(municipal_utils,mun_overlays, county_df, state_df, 'municipal',consts.maps, 'Illinois', paths.maps.utils_html_path)
    #get the population data
    pop_processor = mh.PopulationProcessor(consts.population, paths.population)
    pop_data = pop_processor.load_pop_data()
    [tract_pop, msa_pop, cty_pop] = pop_processor.pop_clean(pop_data, consts.population.geotypes) #msa is not in use for now
    #Interpolate the population
    intp_processor = mh.InterpolationProcessor(consts.population, paths.population)
    intp_pop = intp_processor.process_interpolation(overlays, data = {'tract_pop': tract_pop,'cty_pop': cty_pop}, 
                                                    save = False)
    
    

if __name__ == '__main__':
    main()