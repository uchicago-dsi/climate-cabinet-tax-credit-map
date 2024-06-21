# Census Geographies

All Shapefiles referenced below are available for download through the U.S. Census Bureau's **[web tool](https://www.census.gov/cgi-bin/geo/shapefiles/index.php)** or **[FTP server](https://www2.census.gov/geo/tiger/TIGER2020/)** and have a coordinate reference system of EPSG:4269, the standard for federal agencies.

## Block Groups

**CenPop2020_Mean_BG.txt**. A CSV-formatted text file containing population-weighted centroids for 2020 census block groups.

**Metadata**

|  |  |
|---|---|
| Geographic Coverage | 50 U.S. states, the District of Columbia, and Puerto Rico. |
| Coordinate Reference System | EPSG 4269 |
| Publisher | U.S. Census Bureau |
| Availability | May be downloaded from the Census Bureau's website **[here](https://www.census.gov/geographies/reference-files/time-series/geo/centers-population.2020.html)** by expanding the option "Centers of Population by Block Group" and then searching for and selecting "United States" as an option. |

**Fields**

| Field | Data Type | Non-Null Count | Description | Example |
|---|---|---|---|---|
| Geographic area | string | 20 | The name of the state-equivalent, district, or municipality. The value "Municipality subdivision not defined" refers to offshore water areas that don't below to any district. | `"Northern Islands Municipality"` |
| 2010 | string | 20 | The estimated population for the 2010 census. Formatted as a string with commas. | `"0"` |
| 2020 | string | 20 | The estimated population for the 2020 census. Formatted as a string with commas. | `"7"` |
| Number | string | 19 | The number difference between the 2020 and 2010 populations (2020 - 2010). Formatted as a string with commas. When the computation is not possible, an "X" is used. | `"7"` |
| Percent | float | 19 | The number difference between the 2020 and 2010 populations (2020 - 2010). Formatted as a string with commas. When the computation is not possible, an "X" is used. | `"X"` |

**tl_2020_*_bg.zip.** A collection of TIGER/Line Shapefiles (2020) containing geographic boundaries and metadata for block groups across the 50 U.S. States, District of Columbia, and Island Areas.

**us_block_group_pop_centers_2020.geoparquet.** A GeoParquet file containing pre-processed block group population-weighted centroids for the 50 U.S. states, District of Columbia, and Island Areas.

**us_block_group_population_2020.csv.** A CSV file containing block group level population counts for the 50 U.S. states, District of Columbia, and Island Areas.

## Blocks

**tl_2020_*_tabblock20.zip.** A collection of TIGER/Line Shapefiles (2020) containing geographic boundaries and metadata for tabulation blocks in American Samoa, the Commonwealth of the Northern Mariana Islands, Guam, and the U.S. Virgin Islands.

**us_island_area_block_housing_2020.csv.** A CSV file that lists housing unit counts for each tabulation block in the U.S. Island Areas.

## Counties

**fips_counties.csv.** Associates geography names and FIPS codes (2020) for counties and county-equivalents. Available for download [here](https://www2.census.gov/geo/docs/reference/codes2020/national_county2020.txt).

**tl_2020_us_county.zip.** A TIGER/Line Shapefile (2020) containing geographic boundaries and metadata for the 3,234 U.S. counties and county equivalents (e.g., Louisiana parishes, organized boroughs of Alaska, independent cities, the District of Columbia, Puerto Rican municipalities). Relevant fields include the state and county FIPS codes, `STATEFP` and `COUNTYFP`, which are combined together in the `GEOID` column; the geographic area name, `NAME`; and the name + legal/statistical area description ("LSAD") column, `NAMELSAD` (e.g., "Atlanta city").

**us_county_population_2020.csv.** Total population counts for each U.S. county, as tabulated by the U.S. Census Bureau for the 2020 Census.

## County Subdivisions

**tl_2020_\*\*_cousub.zip.** A collection of TIGER/Line Shapefiles (2020) containing geographic boundaries and metadata for the 36,639 U.S. county subdivisions across the 50 U.S. states, American Samoa, the Commonwealth of the Northern Mariana Islands, Guam, Puerto Rico, and the U.S. Virgin Islands. Relevant fields include the state, county, and county subdivision FIPS codes (`STATEFP`, `COUNTYFP`, and `COUSUBFP`, respectively), which are combined into the `GEOID` column, as well as `NAME` and `NAMELSAD`.

**us_county_subdivision_population_2020.csv.** Total population counts for each U.S. county subdivision, as tabulated by the U.S. Census Bureau for the 2020 Census.

## Government Units

**gov_unit_corrections.json.** Corrections to apply to the U.S. Census Bureau Excel file `Govt_Units_2021_Final.xlsx` during the data-cleaning process (i.e., records to drop, outdated FIPS codes to update, and friendlier names to substitute). Created by University of Chicago Data Science Institute staff members.

**Government_Units_List_Documentation_2021.pdf.** Describes the layout and columns of the Excel file listed below.

**Govt_Units_2021_Final.xlsx.**  A snapshot view of the Census Bureau's master address file for governments. Includes all independent government units and dependent school districts that were active as of fiscal year ending June 30, 2021. The units were extracted from the Governments Master Address File (GMAF) on September 24, 2021. Available for download within a **[zipped file](https://www2.census.gov/programs-surveys/gus/datasets/2021/govt_units_2021.ZIP)** that also contains the above documentation.


## Places

**tl_2020_\*\*_place.zip.** A collection of TIGER/Line Shapefiles (2020) containing geographic boundaries and metadata for the 32,188 Census Bureau places across the 50 U.S. states, American Samoa, the Commonwealth of the Northern Mariana Islands, Guam, Puerto Rico, and the U.S. Virgin Islands. Relevant fields include the state and place FIPS codes (`STATEFP` and `PLACEFP`, respectively), which are combined into the `GEOID` column, as well as `NAME` and `NAMELSAD`.

**us_place_population_2020.csv.** Total population counts for each U.S. place, as tabulated by the U.S. Census Bureau for the 2020 Census.

## States

**fips_states.csv.** Associates geography names and FIPS codes (2020) for states and state-equivalents. Available for download [here](https://www2.census.gov/geo/docs/reference/state.txt).

**tl_2020_us_state.zip.** A TIGER/Line Shapefile for 2020 containing geographic boundaries and metadata for states and state-equivalents.

**us_state_population_2020.csv.** Total population counts for each U.S. state, as tabulated by the U.S. Census Bureau for the 2020 Census.

**Metadata**

|  |  |
|---|---|
| Geographic Coverage | 50 U.S. states, the District of Columbia, and the six territories of American Samoa, Guam, the Commonwealth of the Northern Marina Islands, Puerto Rico, and the U.S. Virgin Islands |
| Coordinate Reference System | EPSG 4269 |
| Publisher | U.S. Census Bureau |
| Availability | May be downloaded through the U.S. Census Bureau's **[web tool](https://www.census.gov/cgi-bin/geo/shapefiles/index.php)** or **[FTP server](https://www2.census.gov/geo/tiger/TIGER2020/)** |


**Fields**

| Field | Data Type | Non-Null Count | Description | Example |
|---|---|---|---|---|
| REGION | string |  | The current region code. | `"3"` |
| DIVISION | string |  | The current division code. | `"5"` |
| STATEFP | string |  | The two-digit, zero-padded state FIPS code. | `"54"` |
| STATEENS | string |  | The ANSI feature code for the state or state-equivalent entity. | `"01779805"` |
| GEOID | string |  | The state identifier, which is the state FIPS code. | `"54"` |
| STUSPS | string |  | The current United States Postal Service abbreviation. | `"WV"` |
| NAME | string |  | The current state name. | `"West Virginia"` |
| LSAD | string |  | The legal/statistical area description code for the state. | `"00"` |
| MTFCC | string |  | The MAF/TIGER feature class code, equal to G4000. | `"G4000"` |
| FUNCSTAT | string |  | The current functional status code. | `"A"` |
| ALAND | integer |  | The current land area. | `62266296765` |
| AWATER | integer |  | The current water area. | `489206049` |
| INTPTLAT | string |  | The current latitude of the state's internal point. Formatted with leading plus and minus signs. | `"+38.6472854"` |
| INTPTLON | string |  | The current longitude of the state's internal point. Formatted with leading plus and minus signs. | `"-080.6183274"` |


## Tracts

**CenPop2020_Mean_TR.txt**. A CSV-formatted text file containing population-weighted centroids for 2020 census tracts.

**tl_2020_\*\*_tract.zip.** A collection of 56 TIGER/Line Shapefiles for 2020, containing a total of 85,528 census tracts.

**Metadata**

|  |  |
|---|---|
| Geographic Coverage | 50 U.S. states, the District of Columbia, and the six territories of American Samoa, Guam, the Commonwealth of the Northern Marina Islands, Puerto Rico, and the U.S. Virgin Islands |
| Coordinate Reference System | EPSG 4269 |
| Publisher | U.S. Census Bureau |
| Availability | May be downloaded through the U.S. Census Bureau's **[web tool](https://www.census.gov/cgi-bin/geo/shapefiles/index.php)** or **[FTP server](https://www2.census.gov/geo/tiger/TIGER2020/)** |


**Fields**

| Field | Data Type | Non-Null Count | Description | Example |
|---|---|---|---|---|
| STATEFP | string |  | The two-digit, zero-padded state FIPS code for 2020. | `"37"` |
| COUNTYFP | string |  | The two-digit, zero-padded county FIPS code for 2020. | `"141"` |
| TRACTCE | string |  | The six-digit, zero-padded census tract code for 2020. | `"920300"` |
| GEOID | string |  | The census tract identifier, which is the state FIPS code, county FIPS code, and tract code concatenated. | `"37141920300"` |
| NAME | string |  | The current census tract name. This is the census tract code converted to an integer or an interger with wo decimals if th elast two characters of the code are not both zeroes. | `"9203"` |
| NAMELSAD | string |  | The legal/statistical area description and the census tract name. | `"Census Tract 9203"` |
| MTFCC | string |  | The MAF/TIGER feature class code, equal to G5020. | `"G5020"` |
| FUNCSTAT | string |  | The current functional status code. | `"S"` |
| ALAND | integer |  | The current land area. | `236115472` |
| AWATER | integer |  | The current water area. | `605423` |
| INTPTLAT | string |  | The current latitude of the 's internal point. Formatted with leading plus and minus signs. | `"+34.6713171"` |
| INTPTLON | string |  | The current longitude of the state's internal point. Formatted with leading plus and minus signs. | `"-078.0020072"` |

**us_census_tract_population_2020.csv.** Total population counts for each U.S. census tract, as tabulated by the U.S. Census Bureau for the 2020 Census.

## Zip Code Tabulation Areas

**tl_2020_us_zcta520.zip**. A TIGER/Line Shapefile for 2020 containing a total of 33,791 ZIP Code Tabulation Areas. It is important to note that ZIP Codes differ from ZCTAs, as **[documented](https://www.census.gov/programs-surveys/geography/guidance/geo-areas/zctas.html)** by the U.S. Census Bureau:

>First introduced in 1963, ZIP Code is a trademark of the USPS created to coordinate mail handling and delivery. The USPS assigns ZIP Code ranges to regional post offices, which in turn assign ZIP Codes to delivery routes. Each delivery route is composed of street networks, and/or individual units with high mail volumes, such as high-rise buildings or individual business locations. Within the Census Bureau’s MAF/TIGER System, ZIP Codes are stored as one component of discrete addresses tied to delivery points, including specific housing unit locations. The result is a point-based dataset unsuitable for mapping and many analysis applications.

>ZCTAs are generalized areal representations of the geographic extent and distribution of the point-based ZIP Codes built using 2020 Census tabulation blocks. The Census Bureau is restricted by Title 13 from releasing individual housing unit addresses or location information to the public, so point-based ZIP Code data are unsuitable for distribution and publication. However, by aggregating the points and extrapolating them to a polygonal-based unit (census tabulation blocks), disclosure concerns can be addressed and “geographic subtraction*” is prevented.

**Metadata**

|  |  |
|---|---|
| Geographic Coverage | 50 U.S. states, the District of Columbia, and the six territories of American Samoa, Guam, the Commonwealth of the Northern Marina Islands, Puerto Rico, and the U.S. Virgin Islands |
| Coordinate Reference System | EPSG 4269 |
| Publisher | U.S. Census Bureau |
| Availability | May be downloaded through the U.S. Census Bureau's **[web tool](https://www.census.gov/cgi-bin/geo/shapefiles/index.php)** or **[FTP server](https://www2.census.gov/geo/tiger/TIGER2020/)** |


**Fields**

| Field | Data Type | Non-Null Count | Description | Example |
|---|---|---|---|---|
| ZCTA5CE20 | string |  | The five-digit ZIP Code Tabulation Area code. | `"35592"` |
| GEOID20 | string |  | The five-digit ZIP Code Tabulation Area code. | `"35592"` |
| CLASSFP20 | string |  | The 2020 Census FIPS 55 class code. | `"B5"` |
| MTFCC20 | string |  | The MAF/TIGER feature class code, equal to G6350. | `"G6350"` |
| FUNCSTAT20 | string |  | The current functional status code. | `"S"` |
| ALAND20 | integer |  | The current land area. | `298552385` |
| AWATER20 | integer |  | The current water area. | `298552385` |
| INTPTLAT20 | string |  | The current latitude of the 's internal point. Formatted with leading plus and minus signs. | `"+33.7427261"` |
| INTPTLON20 | string |  | The current longitude of the state's internal point. Formatted with leading plus and minus signs. | `"-088.0973903"` |


**us_zcta_population_2020.csv.** Total population counts for each U.S. zip code tabulation area (ZCTA), as tabulated by the U.S. Census Bureau for the 2020 Census.