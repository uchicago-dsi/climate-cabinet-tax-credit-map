# Census Bureau

All Shapefiles referenced below are available for download through the U.S. Census Bureau's **[web tool](https://www.census.gov/cgi-bin/geo/shapefiles/index.php)** or **[FTP server](https://www2.census.gov/geo/tiger/TIGER2020/)** and have a coordinate reference system of EPSG:4269, the standard for federal agencies.

## Counties

**tl_2020_us_county.zip.** A TIGER/Line Shapefile (2020) containing geographic boundaries and metadata for the 3,234 U.S. counties and county equivalents (e.g., Louisiana parishes, organized boroughs of Alaska, independent cities, the District of Columbia, Puerto Rican municipalities). Relevant fields include the state and county FIPS codes, `STATEFP` and `COUNTYFP`, which are combined together in the `GEOID` column; the geographic area name, `NAME`; and the name + legal/statistical area description ("LSAD") column, `NAMELSAD` (e.g., "Atlanta city").

## County Subdivisions

**tl_2020_\*\*_cousub.zip.** A collection of TIGER/Line Shapefiles (2020) containing geographic boundaries and metadata for the 36,639 U.S. county subdivisions across the 50 U.S. states, American Samoa, the Commonwealth of the Northern Mariana Islands, Guam, Puerto Rico, and the U.S. Virgin Islands. Relevant fields include the state, county, and county subdivision FIPS codes (`STATEFP`, `COUNTYFP`, and `COUSUBFP`, respectively), which are combined into the `GEOID` column, as well as `NAME` and `NAMELSAD`.

## FIPS Codes

**fips_counties.csv.** Associates geography names and FIPS codes (2020) for counties and county-equivalents. Available for download [here](https://www2.census.gov/geo/docs/reference/codes2020/national_county2020.txt).

**fips_states.csv.** Associates geography names and FIPS codes (2020) for states and state-equivalents. Available for download [here](https://www2.census.gov/geo/docs/reference/state.txt).

## Government Units

**Government_Units_List_Documentation_2021.pdf.** Describes the layout and columns of the Excel file listed below.

**Govt_Units_2021_Final.xlsx.**  A snapshot view of the Census Bureau's master address file for governments. Includes all independent government units and dependent school districts that were active as of fiscal year ending June 30, 2021. The units were extracted from the Governments Master Address File (GMAF) on September 24, 2021. Available for download within a **[zipped file](https://www2.census.gov/programs-surveys/gus/datasets/2021/govt_units_2021.ZIP)** that also contains the above documentation.

## Places

**tl_2020_\*\*_place.zip.** A collection of TIGER/Line Shapefiles (2020) containing geographic boundaries and metadata for the 32,188 Census Bureau places across the 50 U.S. states, American Samoa, the Commonwealth of the Northern Mariana Islands, Guam, Puerto Rico, and the U.S. Virgin Islands. Relevant fields include the state and place FIPS codes (`STATEFP` and `PLACEFP`, respectively), which are combined into the `GEOID` column, as well as `NAME` and `NAMELSAD`.

## Population

**american-samoa-phc-table01.csv.** Population counts at the national, county, district, and island level from the 2010 and 2020 censuses of American Samoa. Available for download from the U.S. Census Bureau **[here](https://www.census.gov/data/tables/2020/dec/2020-american-samoa.html#pophousingcounts)**.

**CenPop2020_Mean_BG.txt.** A CSV-formatted text file containing population-weighted centroids for 2020 census block groups. Published by the U.S. Census Bureau. Available for download **[here](https://www.census.gov/geographies/reference-files/time-series/geo/centers-population.2020.html)** by expanding the option "Centers of Population by Block Group" and then searching for and selecting "United States" as an option.

**commonwealth-northern-mariana-islands-phc-table01.csv.** Population counts at the national, district, municipality, and offshore water areas from the 2010 and 2020 censuses of the Commonwealth of the Northern Mariana Islands. Available for download from the U.S. Census Bureau **[here](https://www.census.gov/data/tables/2020/dec/2020-commonwealth-northern-mariana-islands.html)**.

**guam-phc-table01.csv.** Population counts at the national, municipality, and offshore water areas from the 2010 and 2020 censuses of Guam. Available for download from the U.S. Census Bureau [here](https://www.census.gov/data/tables/2020/dec/2020-guam.html).

**us-virgin-islands-phc-table01.csv.** Population counts at the national, island, district, town, census designated place (CDP), and offshore water areas from the 2010 and 2020 censuses of the U.S. Virgin Islands. Available for download from the U.S. Census Bureau [here](https://www.census.gov/data/tables/2020/dec/2020-guam.html).

## States

**tl_2020_us_state.zip.** A TIGER/Line Shapefile (2020) containing geographic boundaries and metadata for the 50 U.S. states and their equivalents (i.e., the District of Columbia and the six territories of American Samoa, Guam, the Commonwealth of the Northern Marina Islands, Puerto Rico, and the U.S. Virgin Islands). Relevant fields for data processing include `NAME` and the **[FIPS code](https://transition.fcc.gov/oet/info/maps/census/fips/fips.txt)**, `STATEFP`, (also represented by the field `GEOID`).

## Tracts

**tl_2020_\*\*_tract.zip.** A collection of 56 TIGER/Line Shapefiles (2020) containing 85,528 census tracts across the 50 U.S. states, American Samoa, the Commonwealth of the Northern Mariana Islands, Guam, Puerto Rico, and the U.S. Virgin Islands. Relevant columns include the FIPS codes for states (`STATEFP`), counties (`COUNTYFP`), and tracts (`TRACTCE`); the unique geography identifier, created from FIPS codes (`GEOID`); and the name + legal/statistical area description (`NAMELSAD`).

## Zip Code Tabulation Areas

**tl_2020_us_zcta520.zip.** A TIGER/Line Shapefile (2020) for the 33,791 ZIP Code Tabulation Areas across the 50 U.S. States, District of Columbia, and six U.S. territories recognized by the U.S. Census Bureau. Relevant fields include the zip code tabulation area (ZCTA) number (`ZCTA5CE20` or `GEOID20`), which represents a valid USPS ZIP Code as of January, 1, 2020. It is important to note that ZIP Codes differ from ZCTAs, as **[documented](https://www.census.gov/programs-surveys/geography/guidance/geo-areas/zctas.html)** by the U.S. Census Bureau.