## Scripts
What do the scripts do: <br>
#### 1. `preprocess_helper.py`:
- Contains the functions needed to load, preprocess the data or to save them as csv/shp files.

#### 2. `cleanup_helper.py`:
- Contains the functions needed to perform additional cleanup specific to each community and returns the cleaned up version of respective datasets.

#### 3. `overlay_map_helper.py`:
- Contains the functions needed to make spatial overlays and generate the folium plots for those overlays for both rural cooperatives and municipal/public utilities.
- The maps will be saved as HTML files on the disk.

#### 4. `tract_file_scraper.py`:
- The tract level shape files for all the tracts in the nation will be obtained from the scraper script:
    - To do this, might have to use a web scraper like BS4 since all tracts cannot be downloaded at once.
    - Once downloaded and merged all the tracts into a single geo Dataframe, save it to the disk


### Additional Deatils: 
#### 1. Electric Retail Service Territories data cleanup process:
- Loads the **Electric Retial Service Territories** shape file downlaoded from :  [Homeland Infrastructure Foundation-Level Data (HIFLD)](https://hifld-geoplatform.opendata.arcgis.com/datasets/geoplatform::electric-retail-service-territories-2/explore?location=21.841288%2C-93.233909%2C3.97)
- Cleans up the `GeoDataFrame` by dropping, renaming and making columns. Then merges the dataframe with a CSV containing the Abbreviations and State names to get the state names.
- The dataset will be filtered to contain only the Rural Coops or Municipal Utilites.

#### 2. Justice40 communities data cleanup process`:
- Loads the **Justice40 Disadvantaged Communitites** shape file downloaded from : [Climate and Economic Justice Screening Tool](https://screeningtool.geoplatform.gov/en/#4.91/37.6/-92.43)
- Cleans up the `GeoDataFrame` by dropping, renaming and making new columns.

#### 3. Energy communities data cleanup process:
[Ref: Energy Community definitions by IRA](https://energycommunities.gov/energy-community-tax-credit-bonus/)
- Loads the energy community shape files downloaded from [National Energy Technology Laboratory](https://edx.netl.doe.gov/dataset/ira-energy-community-data-layers)
- Both the coal closure and fossil fuel employment datasets will be cleaned up by dropping, renaming and making columns.

#### 4. Low Income communities data cleanup process:
[Ref: ArcGIS Low Income Communities](https://www.esri.com/arcgis-blog/products/arcgis-living-atlas/decision-support/mapping-low-income-communities-in-the-us/)  
*Sources*: [Shape file source](https://www.census.gov/cgi-bin/geo/shapefiles/index.php), [Census Tracts](https://www2.census.gov/geo/tiger/TIGER2020/TRACT/), [Reports from Social Explorer](https://www.socialexplorer.com/reports/socialexplorer/en/)  
- Dowload the datasets `Table B17020: Poverty Status in the Past 12 Months - Tracts` and `Table B19113: Median Family Income in the Past 12 Months (in 2020 inflation-adjusted dollars) - Tracts, Metropolitan area, State`
- Flter the poverty, median income (tracts, state, MSA) datasets to contain only the needed columns and make a calculated columns as needed.
- Merge the tract and state level median incomes to have the `st_med_income` within the same dataset and save it to the disk.
- Since MSA dataframe has no attribute to join with other, perform spatial join using the shapefile, merge the `msa_med_income` column and save it as a shape file on the disk.
- MSA's have geomtries to spatially join with the tracts, but the poverty and income datasets do not.
- Used the merged tracts resulted from the `tract_file_scraper.py` script to use for the merging.
- Merge all the datasets into a single shape file.
    - First the tract level median income dataset will be merged with the merged tracts file then with the poverty dataset to obtain the geometries of the data.
    - Then spatial join between the MSA shapefile and the merged geo dataframe will be made.
- The geometries will be dissolved by the tractId since there would be duplicates appearing from the spatial join.(It's possible that some tracts have multiple overlapping MSA geometries.)
-The conditions wil be applied for classifying a tract as a low income community and the final data is saved.

#### 5. Distressed Communities data cleanup process:
- Data was purchased from [Economic Innovation Group](https://eig.org/distressed-communities/get-the-data/dci-academic-dataset/) which has the quintile scores that are needed to classify a zipcode/county as Distressed community.
- Download the census shape file at a zipcode level for 2020 and perform the spatial join to get the geometries.