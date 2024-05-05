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

### American Samoa

A CSV file (`"american-samoa-phc-table01.csv"`) containing population counts at the national, county, district, and island level from the 2010 and 2020 censuses of American Samoa. 

**Metadata**

|  |  |
|---|---|
| Geographic Coverage | American Samoa |
| Coordinate Reference System | EPSG 4269 |
| Publisher | U.S. Census Bureau |
| Availability | May be downloaded from the Census Bureau's website **[here](https://www.census.gov/data/tables/2020/dec/2020-american-samoa.html#pophousingcounts)**. |

**Fields**

| Field | Data Type | Non-Null Count | Description | Example |
|---|---|---|---|---|
| Geographic area | string | 20 | The name of the state-equivalent, district, county, or island. | `"Eastern District"` |
| 2010 | string | 20 | The estimated population for the 2010 census. Formatted as a string with commas. | `"23,030"` |
| 2020 | string | 20 | The estimated population for the 2020 census. Formatted as a string with commas. | `"17,059"` |
| Number | string | 19 | The number difference between the 2020 and 2010 populations (2020 - 2010). Formatted as a string with commas. When the computation is not possible, an "X" is used. | `"-5,809"` |
| Percent | float | 19 | The number difference between the 2020 and 2010 populations (2020 - 2010). Formatted as a string with commas. When the computation is not possible, an "X" is used. | `-10.5` |


### Block Group Centers of Population

A CSV-formatted text file (`"CenPop2020_Mean_BG.txt"`) containing population-weighted centroids for 2020 census block groups. |
| Geographic Coverage | 50 U.S. states, the District of Columbia, and Puerto Rico.

**Metadata**

|  |  |
|---|---|
| Coordinate Reference System | EPSG 4269 |
| Publisher | U.S. Census Bureau |
| Availability | May be downloaded from the Census Bureau's website **[here](https://www.census.gov/geographies/reference-files/time-series/geo/centers-population.2020.html)** by expanding the option "Centers of Population by Block Group" and then searching for and selecting "United States" as an option. |

**Fields**

| Field      	| Data Type 	| Non-Null Count 	| Description                                                                                                 	| Example       	|
|------------	|-----------	|----------------	|-------------------------------------------------------------------------------------------------------------	|---------------	|
| STATEFP    	| string    	| 242,335        	| The two-digit, zero-padded state FIPS code.                                                                 	| `"01"`          	|
| COUNTYFP   	| string    	| 242,335        	| The three-digit, zero-padded county FIPS code.                                                              	| `"001"`         	|
| TRACTCE    	| string    	| 242,335        	| The six-digit, zero-padded census tract code.                                                               	| `"020100"`      	|
| BLKGRPCE   	| string    	| 242,335        	| The one-digit census block group code.                                                                      	| `"1"`           	|
| POPULATION 	| integer   	| 242,335        	| The 2020 Census population tabulated for the census tract.                                                  	| `575`           	|
| LATITUDE   	| string    	| 242,335        	| The latitude coordinate for the center of population for the block group. Prefixed with a "+" or "-" sign.  	| `"+32.464466"`  	|
| LONGITUDE  	| string    	| 242,335        	| The longitude coordinate for the center of population for the block group. Prefixed with a "+" or "-" sign. 	| `"-086.486302"` 	|

### Commonwealth of the Northern Mariana Islands

A CSV file (`"commonwealth-northern-mariana-islands-phc-table01.csv"`) containing population counts at the national, district, municipality, and offshore water areas from the 2010 and 2020 censuses of the Commonwealth of the Northern Mariana Islands.

**Metadata**

|  |  |
|---|---|
| Geographic Coverage | Commonwealth of the Northern Mariana Islands |
| Coordinate Reference System | EPSG 4269 |
| Publisher | U.S. Census Bureau |
| Availability | May be downloaded from the Census Bureau's website **[here](https://www.census.gov/data/tables/2020/dec/2020-commonwealth-northern-mariana-islands.html)**. |


**Fields**

| Field | Data Type | Non-Null Count | Description | Example |
|---|---|---|---|---|
| Geographic area | string | 20 | The name of the state-equivalent, district, or municipality. The value "Municipality subdivision not defined" refers to offshore water areas that don't below to any district. | `"Northern Islands Municipality"` |
| 2010 | string | 20 | The estimated population for the 2010 census. Formatted as a string with commas. | `"0"` |
| 2020 | string | 20 | The estimated population for the 2020 census. Formatted as a string with commas. | `"7"` |
| Number | string | 19 | The number difference between the 2020 and 2010 populations (2020 - 2010). Formatted as a string with commas. When the computation is not possible, an "X" is used. | `"7"` |
| Percent | float | 19 | The number difference between the 2020 and 2010 populations (2020 - 2010). Formatted as a string with commas. When the computation is not possible, an "X" is used. | `"X"` |


### Guam

A CSV file (`"guam-phc-table01.csv"`) containing population counts at the national, municipality, and offshort water areas from the 2010 and 2020 censuses of Guam.

**Metadata**

|  |  |
|---|---|
| Geographic Coverage | Guam |
| Coordinate Reference System | EPSG 4269 |
| Publisher | U.S. Census Bureau |
| Availability | May be downloaded from the Census Bureau's website **[here](https://www.census.gov/data/tables/2020/dec/2020-guam.html)**. |

**Fields**

| Field | Data Type | Non-Null Count | Description | Example |
|---|---|---|---|---|
| Geographic area | string | 22 | The name of the state-equivalent, district, or municipality. The value "County subdivision not defined" refers to offshore water areas that don't below to any municipality. | `"Agana Heights municipality"` |
| 2010 | string | 22 | The estimated population for the 2010 census. Formatted as a string with commas. | `"3,808"` |
| 2020 | string | 22 | The estimated population for the 2020 census. Formatted as a string with commas. | `"3,673"` |
| Number | string | 22 | The number difference between the 2020 and 2010 populations (2020 - 2010). Formatted as a string with commas. When the computation is not possible, an "X" is used. | `"-135"` |
| Percent | float | 21s | The number difference between the 2020 and 2010 populations (2020 - 2010). Formatted as a string with commas. When the computation is not possible, an "X" is used. | `"-3.5"` |


### U.S. Virgin Islands

A CSV file (`"us-virgin-islands-phc-table01.csv"`) containing population counts at the state-equivalent, island, district, town, census designated place (CDP), and offshort water areas from the 2010 and 2020 censuses of the U.S. Virgin Islands.

**Metadata**

|  |  |
|---|---|
| Geographic Coverage | U.S. Virgin Islands |
| Coordinate Reference System | EPSG 4269 |
| Publisher | U.S. Census Bureau |
| Availability | May be downloaded from the Census Bureau's website **[here](https://www.census.gov/data/tables/2020/dec/2020-us-virgin-islands.html)**. |

**Fields**

| Field | Data Type | Non-Null Count | Description | Example |
|---|---|---|---|---|
| Geographic area | string | 37 | The name of the state-equivalent, island, district, town, census-designated place (CDP), or offshore water area. The value "Island subdivision not defined" refers to offshore water areas and small uninhabitated islands not assigned to any subdistrict. | `"St. Croix Island"` |
| 2010 | string | 37 | The estimated population for the 2010 census. Formatted as a string with commas. | `"50,601"` |
| 2020 | string | 37 | The estimated population for the 2020 census. Formatted as a string with commas. | `"41,004"` |
| Number | string | 37 | The number difference between the 2020 and 2010 populations (2020 - 2010). Formatted as a string with commas. When the computation is not possible, an "X" is used. | `"-9,597"` |
| Percent | float | 37 | The number difference between the 2020 and 2010 populations (2020 - 2010). When the computation is not possible, an "X" is used. | `"-19.0"` |


## States

A TIGER/Line Shapefile for 2020 (`"tl_2020_us_state.zip"`) containing geographic boundaries and metadata for states and state-equivalents.

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

A collection of 56 TIGER/Line Shapefiles (`"tl_2020_**_tract.zip"`) for 2020 containing a total of 85,528 census tracts.

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

## Zip Code Tabulation Areas

A TIGER/Line Shapefile (`"tl_2020_us_zcta520.zip"`) for 2020 containing a total of 33,791 ZIP Code Tabulation Areas. It is important to note that ZIP Codes differ from ZCTAs, as **[documented](https://www.census.gov/programs-surveys/geography/guidance/geo-areas/zctas.html)** by the U.S. Census Bureau:

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