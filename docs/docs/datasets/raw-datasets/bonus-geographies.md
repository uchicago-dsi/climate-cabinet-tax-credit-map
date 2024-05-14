# Bonus Geographies

## Distressed

### Distressed Community Index Scores

**DCI-2016-2020-Academic-Non-profit-Government-Scores-Only.xlsx.** An Excel file of distressed community index (DCI) scores using 2016-2020 American Community Survey data and the Census Bureau’s Business Patterns datasets for 2016 and 2020.

**Metadata**

|  |  |
|---|---|
| Geographic Coverage | 50 U.S. States and District of Columbia |
| Coordinate Reference System | N/A |
| Publisher | Economic Innovation Group (EIG) |
| Availability | May be **[purchased and downloaded](https://eig.org/distressed-communities/get-the-data/dci-academic-dataset/)** as scores only for $100 USD. |

**Fields**

| Field | Data Type | Non-Null Count | Description | Example |
|---|---|---|---|---|
| Zipcode | integer | 26,059 | The ZCTA code. Leading zeroes (e.g., Connecticut, Massachusetts) are not displayed, so length ranges from four to five digits. | `1001` |
| Metro area | string | 15,894 | The primary metropolitan area of the ZCTA. | `"Springfield, MA"` |
| County | string | 26,059 | The primary county of the ZCTA. | `"Hampden County, Massachusetts"` |
| State | string | 26,059 | The primary state of the ZCTA. | `"Massachusetts"` |
| Census Region | string | 26,059 | The official census region: "Midwest", "Northeast", "South", or "West". | `"Northeast"` |
| County Type | string | 26,059 | The urbanization level of the county: "Exurban", "Large urban", "Metro rural", "Nonmetro rural", "Small urban", or "Suburban". | `"Small urban"` |
| Total Population | integer | 26,059 | The estimated population in the ZCTA. | `16064` |
| Distress Score | float | 26,059 | The normalized distress score. Ranges from 0 to 100. | `35.016693` |
| Quintile (5=Distressed) | integer | 26,059 | The distress score percentile for the ZCTA. "Distressed" ZCTAs have a score in the upper quintile (i.e., the top 20 percent). | `2` |

## Energy

### Coal Closure Census Tracts

**ira_coal_closure_energy_comm_2023v2.zip.** A Shapefile of 2020 census tracts and directly adjoining tracts that have had coal mine closures since 1999 or coal-fired electric generating unit retirements since 2009. For more information, please see the FAQs **[here](https://energycommunities.gov/energy-community-tax-credit-bonus-faqs/)**.

**Metadata**

|  |  |
|---|---|
| Geographic Coverage | 45 U.S. States and District of Columbia |
| Coordinate Reference System | EPSG:4269 |
| Publisher | National Energy Technology Laboratory (NETL), U.S. Department of Energy |
| Availability | Available for download from the **[Energy Data eXchange](https://edx.netl.doe.gov/dataset/ira-energy-community-data-layers)**. |

**Fields**

| Field | Data Type | Non-Null Count | Description | Example |
|---|---|---|---|---|
| AFFGEOID_T | string | 4,191 | The U.S. Census Bureau's unique identifier (GEOID) for the census tract. | `"1400000US01003010100"` |
| fipstate_2 | string | 4,191 | The two-digit FIPS code for the larger state. | `"01"` |
| fipscounty_ | string | 4,191 | The three-digit FIPS code for the larger county. | `"003"` |
| geoid_coun | string | 4,191 | The five-digit GEOID for the larger county. A combination of the FIPS codes for the state and county. | `"01003"` |
| fiptract_2 | string | 4,191 | The six-digit FIPS code for the census tract. | `"010100"` |
| geoid_trac | string | 4,191 | The 11-digit GEOID for the census tract. A combination of the FIPS codes for the state, county, and tract. | `"01003010100"` |
| Mine_Qual | string | 4,191 | A binary variable indicating whether the census tract qualifies as an energy community on the basis of having a coal mine close after 1999. | `"0"` |
| Generator_| string | 4,191 | A binary variable indicating whether the census tract qualifies as an energy community on the basis of retiring a coal-fired electric generating unit after 2009. | `"0"` |
| Neighbor_Q| string | 4,191 | A binary variable indicating whether the census tract qualifies as an energy community on the basis of directly bordering another tract that had a coal mine closure after 1999 or coal-fired electric generating unit retirement after 2009. | `"1"` |
| Mine_Qual | string | 4,191 | A binary variable indicating whether the census tract qualifies as an energy community on the basis of having a coal mine close after 1999. | `"0"` |
| State_Name | string | 4,191 | The name of the larger state. | `"Alabama"` |
| County_Nam | string | 4,191 | The name of the larger county. | `"Baldwin County"` |
| CensusTrac | string | 4,191 | The name of the census tract. | `"Census Tract 101"` |
| Mine_Closu | string | 4,191 | A reader-friendly version of the binary field `Mine_Qual`. Either "Yes" or "No". | `"No"` |
| Generator1 | string | 4,191 | A reader-friendly version of the binary field `Generator1`. Either "Yes" or "No". | `"No"` |
| Adjacent_t | string | 4,191 | A reader-friendly version of the binary field `Neighbor_Q`. Either "Yes" or "No". | `"Yes"` |
| Tract_Stat | string | 4,191 | A reader-friendly explanation of why the tract is an energy community. Choices include: "is an energy community because it directly adjoins a census tract with a qualifying coal closure", "is an energy community due to a coal mine closure", "is an energy community due to a coal-fired electric generating unit retirement", and "is an energy community due to a coal-fired electric generating unit retirement and coal mine closure". | `"is an energy community due to a coal-fired electric generating unit retirement and coal mine closure"` |
| date_last_ | string | 4,191 | The date the data was last updated. | `"2023-05-23"` |
| dataset_ve | float | 4,191 | The current version of the dataset. | `2023.2` |
| record_add | string | 4,191 | The date the record was add to the dataset. | `"2023-03-28"` |
| Symbol | string | 4,191 | Either "Census tract directly adjoining a census tract with a coal closure" or "Census tract with a coal closure". | `"Census tract directly adjoining a census tract with a coal closure"` |
| Shape_Leng | float | 4,191 | The length of the perimeter of the census tract in meters after removing coastal waters. | `1.700086` |
| Shape_Area | string | 4,191 | The area of the census tract in square meters after removing coastal waters. | `0.09541` |


### Fossil Fuel Unemployment MSAs and Non-MSAs

**msa_nmsa_fee_ec_status_2023v2.zip.** A Shapefile of metropolitan statistical areas (MSAs) and non-metropolitan statistical areas (non-MSAs) that meet up to two criteria: (1) having least one year since 2009, 0.17% or greater direct employment related to extraction, processing, transport, or storage of coal, oil, or natural gas (the fossil fuel employment (FFE) threshold) and (2) having an unemployment rate for 2022 that is equal to or greater than the national average unemployment rate for 2022. These MSAs and non-MSAs that meet both criteria are energy communities as of January 1, 2023, and will maintain that status until the unemployment rates for 2023 become available and a new list of energy communities is provided.  For more information, please see the FAQs **[here](https://energycommunities.gov/energy-community-tax-credit-bonus-faqs/)**..

**Metadata**

|  |  |
|---|---|
| Geographic Coverage | 37 U.S. States, Puerto Rico, and the U.S. Virgin Islands |
| Coordinate Reference System | EPSG:4269 |
| Publisher | National Energy Technology Laboratory (NETL), U.S. Department of Energy |
| Availability | Available for download from the **[Energy Data eXchange](https://edx.netl.doe.gov/dataset/ira-energy-community-data-layers)**. |

**Fields**

| Field | Data Type | Non-Null Count | Description | Example |
|---|---|---|---|---|
| ObjectID | integer | 1,505 | The primary key assigned to the record. | `1` |
| AFFGEOID_C | string | 1,505 | The U.S. Census Bureau's unique identifier (GEOID) for the county. | `"0500000US01007"` |
| fipstate_2 | string | 1,505 | The two-digit FIPS code for the larger state. | `"01"` |
| fipscty_20 | string | 1,505 | The three-digit FIPS code for the larger county. | `"007"` |
| geoid_cty_ | string | 1,505 | The five-digit GEOID for the larger county. A combination of the FIPS codes for the state and county. | `"01007"` |
| county_nam | string | 1,505 | The name of the larger county. | `"Bibb County"` |
| state_name | string | 1,505 | The name of the larger state. | `"Alabama"` |
| MSA_area_I | float | 1,505 | The area id for each Metropolitan/Non-Metropolitan Statistical Area (MSA/Non-MSA). | `13820.0` |
| MSA_area_n | float | 1,505 | The name for each Metropolitan/Non-Metropolitan Statistical Area (MSA/Non-MSA). | `"Birmingham-Hoover, AL"` |
| ffe_ind_qu | float | 1,505 | A binary variable indicating whether the county is in an MSA or non-MSA that meets the 0.17 percent threshold for fossil fuel employment. | `1.0` |
| ec_ind_qua | float | 1,505 | A binary variable indicating whether the county is in an MSA or non-MSA that meets _both_ the 0.17 percent threshold for fossil fuel employment and the unemployment rate requirement. | `1.0` |
| msa_qual | float | 1,505 | Indicates whether the county is in an MSA (`"MSA"`) or a Non-MSA (`"Non_MSA"`). | `"MSA"` |
| FEE_qual_s | string | 1,505 | A reader-friendly version of the binary field `ffe_ind_qu`. Either "Yes" or "No". | `"Yes"` |
| EC_qual_st | string | 1,505 | A reader-friendly version of the binary field `ec_ind_qua`. Either "Yes" or "No". | `"No"` |
| Label_FEE | string | 1,505 | A reader-friendly interpretation of the `FEE_qual_s` field. Choices include: "only meets the FFE threshold (not an energy community)" or `None`. | `"only meets the FFE threshold (not an energy community)"` |
| Label_FEE | string | 1,505 | A reader-friendly interpretation of the `EC_qual_st` field. Choices include: "is an energy community, as it meets both the Fossil Fuel Employment (FFE) threshold and the unemployment rate requirement" or "is not an energy community, as it does not meet both the Fossil Fuel Employment (FFE) threshold and the unemployment rate requirement". | `"is not an energy community, as it does not meet both the Fossil Fuel Employment (FFE) threshold and the unemployment rate requirement"` |
| MSA_NMSA_L | string | 1,505 | The name of the MSA or non-MSA that includes its legal statistical description. | `"Birmingham-Hoover, AL metropolitan statistical area (MSA)"` |
| date_last_ | string | 1,505 | The date the data was last updated. | `"2023-05-30"` |
| dataset_ve | float | 1,505 | The current version of the dataset. | `2023.2` |
| date_recor | string | 1,505 | The date the record was add to the dataset. | `"2023-04-03"` |
| Shape_Leng | float | 1,505 | The length of the perimeter of the county. | `1.88752` |
| Shape_Area | string | 1,505 | The area of the county. | `0.156472` |

## Justice40

### Justice40 Census Tracts

**usa.zip.** A zipped shapefile containing all U.S. census tracts for 2010 (74,134 records), of which 27,248 are classified as a Justice40 community.

**Metadata**

|  |  |
|---|---|
| Geographic Coverage | 50 U.S. states, the District of Columbia, and the six territories of American Samoa, Guam, the Commonwealth of the Northern Marina Islands, Puerto Rico, and the U.S. Virgin Islands |
| Coordinate Reference System | EPSG:4326 |
| Publisher | Council on Environmental Quality, Executive Office of the President |
| Availability | Downloaded from the **[Climate and Economic Justice Screening Tool](https://screeningtool.geoplatform.gov/en/downloads)**. |

**Fields**

| Field | Data Type | Non-Null Count | Description | Example |
|---|---|---|---|---|
| GEOID10 | string | 74,134 | The Census Bureau's unique identifier (GEOID) for the 2010 census tract | `"1073001100"` |
| SF | string | 74,134 | State/Territory | `"Alabama"` |
| CF | string | 74,002 | County Name | `"Jefferson County"` |
| DF_PFS | float | 70,313 | Diagnosed diabetes among adults aged greater than or equal to 18 years (percentile) | `0.96` |
| AF_PFS | float | 70,313 | Current asthma among adults aged greater than or equal to 18 years (percentile) | `0.85` |
| HDF_PFS | float | 70,313 | Coronary heart disease among adults aged greater than or equal to 18 years (percentile) | `0.72` |
| DSF_PFS | float | 73,395 | Diesel particulate matter exposure (percentile) | `0.84` |
| EBF_PFS | float | 73,080 | Energy burden (percentile) | `0.86` |
| EALR_PFS | float | 49,978 | Expected agricultural loss rate (Natural Hazards Risk Index) (percentile) | `0.21` |
| EBLR_PFS | float | 72,687 | Expected building loss rate (Natural Hazards Risk Index) (percentile) | `0.78` |
| EPLR_PFS | float | 72,322 | Expected population loss rate (Natural Hazards Risk Index) (percentile) | `0.61` |
| HBF_PFS | float | 72,976 | Housing burden (percent) (percentile) | `0.64` |
| LLEF_PFS | float | 67,148 | Low life expectancy (percentile) | `0.97` |
| LIF_PFS | float | 72,202 | Linguistic isolation (percent) (percentile) | `0.12` |
| LMI_PFS | float | 69,113 | Low median household income as a percent of area median income (percentile) | `0.82` |
| PM25F_PFS | float | 72,259 | PM2.5 in the air (percentile) | `0.82` |
| HSEF | float | 73,255 | Percent individuals age 25 or over with less than high school degree | `0.08` |
| P100_PFS | float | 73,124 | Percent of individuals < 100% Federal Poverty Line (percentile) | `0.62` |
| P200_I_PFS | float | 73,273 | Percent of individuals below 200% Federal Poverty Line, imputed and adjusted (percentile) | `0.6` |
| AJDLI_ET | integer | 74,134 | Meets the less stringent low income criterion for the adjacency index? | `1` |
| LPF_PFS | float | 73,976 | Percent pre-1960s housing (lead paint indicator) (percentile) | `0.39` |
| KP_PFS | float | 72,976 | Share of homes with no kitchen or indoor plumbing (percent) (percentile) | `0.21` |
| NPL_PFS | float | 73,976 | Proximity to NPL sites (percentile) | `0.75` |
| RMP_PFS | float | 73,976 | Proximity to Risk Management Plan (RMP) facilities (percentile) | `0.9` |
| TSDF_PFS | float | 73,976 | Proximity to hazardous waste sites (percentile) | `0.48` |
| TPF | float | 74,094 | Total population | `4781` |
| TF_PFS | float | 71,300 | Traffic proximity and volume (percentile) | `0.39` |
| UF_PFS | float | 73,161 | Unemployment (percent) (percentile) | `0.02` |
| WF_PFS | float | 54,004 | Wastewater discharge (percentile) | `0.96` |
| UST_PFS | float | 73,976 | Leaky underground storage tanks (percentile) | `0.52` |
| N_WTR | integer | 74,134 | Water Factor (Definition N) | `0` |
| N_WKFC | integer | 74,134 | Workforce Factor (Definition N) | `0` |
| N_CLT | integer | 74,134 | Climate Factor (Definition N) | `0` |
| N_ENY | integer | 74,134 | Energy Factor (Definition N) | `0` |
| N_TRN | integer | 74,134 | Transportation Factor (Definition N) | `0` |
| N_HSG | integer | 74,134 | Housing Factor (Definition N) | `0` |
| N_PLN | integer | 74,134 | Pollution Factor (Definition N) | `0` |
| N_HLTH | integer | 74,134 | Health Factor (Definition N) | `0` |
| SN_C | integer | 74,134 | Definition N community, including adjacency index tracts | `0` |
| SN_T | string | 2,206 | Identified as disadvantaged due to tribal overlap | `None` |
| DLI | integer | 74,134 | Greater than or equal to the 90th percentile for diabetes and is low income? | `0` |
| ALI | integer | 74,134 | Greater than or equal to the 90th percentile for asthma and is low income? | `0` |
| PLHSE | integer | 74,134 | Greater than or equal to the 90th percentile for households at or below 100% federal poverty level and has low HS attainment? | `0` |
| LMILHSE | integer | 74,134 | Greater than or equal to the 90th percentile for low median household income as a percent of area median income and has low HS attainment? | `0` |
| ULHSE | integer | 74,134 | Greater than or equal to the 90th percentile for unemployment and has low HS attainment? | `0` |
| EPL_ET | integer | 74,134 | Greater than or equal to the 90th percentile for expected population loss | `0` |
| EAL_ET | integer | 74,134 | Greater than or equal to the 90th percentile for expected agricultural loss | `0` |
| EBL_ET | integer | 74,134 | Greater than or equal to the 90th percentile for expected building loss | `0` |
| EB_ET | integer | 74,134 | Greater than or equal to the 90th percentile for energy burden | `0` |
| PM25_ET | integer | 74,134 | Greater than or equal to the 90th percentile for pm2.5 exposure | `0` |
| DS_ET | integer | 74,134 | Greater than or equal to the 90th percentile for diesel particulate matter | `0` |
| TP_ET | integer | 74,134 | Greater than or equal to the 90th percentile for traffic proximity | `0` |
| LPP_ET | integer | 74,134 | Greater than or equal to the 90th percentile for lead paint and the median house value is less than 90th percentile | `0` |
| HRS_ET | string | 12,888 | Tract-level redlining score meets or exceeds 3.25 | `1` |
| KP_ET | integer | 74,134 | Greater than or equal to the 90th percentile for share of homes without indoor plumbing or a kitchen | `0` |
| HB_ET | integer | 74,134 | Greater than or equal to the 90th percentile for housing burden | `0` |
| RMP_ET | integer | 74,134 | Greater than or equal to the 90th percentile for RMP proximity | `1` |
| NPL_ET | integer | 74,134 | Greater than or equal to the 90th percentile for NPL (superfund sites) proximity | `0` |
| TSDF_ET | integer | 74,134 | Greater than or equal to the 90th percentile for proximity to hazardous waste sites | `0` |
| WD_ET | integer | 74,134 | Greater than or equal to the 90th percentile for wastewater discharge | `1` |
| UST_ET | integer | 74,134 | Greater than or equal to the 90th percentile for leaky underwater storage tanks | `0` |
| DB_ET | integer | 74,134 | Greater than or equal to the 90th percentile for diabetes | `1` |
| A_ET | integer | 74,134 | Greater than or equal to the 90th percentile for asthma | `0` |
| HD_ET | integer | 74,134 | Greater than or equal to the 90th percentile for heart disease | `0` |
| LLE_ET | integer | 74,134 | Greater than or equal to the 90th percentile for low life expectancy | `1` |
| UN_ET | integer | 74,134 | Greater than or equal to the 90th percentile for unemployment | `0` |
| LISO_ET | integer | 74,134 | Greater than or equal to the 90th percentile for households in linguistic isolation | `0` |
| POV_ET | integer | 74,134 | Greater than or equal to the 90th percentile for households at or below 100% federal poverty level | `0` |
| LMI_ET | integer | 74,134 | Greater than or equal to the 90th percentile for low median household income as a percent of area median income | `0` |
| IA_LMI_ET | integer | 74,134 | Low median household income as a percent of territory median income in 2009 exceeds 90th percentile | `0` |
| IA_UN_ET | integer | 74,134 | Unemployment (percent) in 2009 exceeds 90th percentile | `0` |
| IA_POV_ET | integer | 74,134 | Percentage households below 100% of federal poverty line in 2009 exceeds 90th percentile | `0` |
| TC | integer | 74,134 | Total threshold criteria exceeded | `0` |
| CC | float | 74,134 | Total categories exceeded | `0` |
| IAULHSE | integer | 74,134 | Greater than or equal to the 90th percentile for unemployment and has low HS education in 2009 (island areas)? | `0` |
| IAPLHSE | integer | 74,134 | Greater than or equal to the 90th percentile for households at or below 100% federal poverty level and has low HS education in 2009 (island areas)? | `0` |
| IALMILHSE | integer | 74,134 | Greater than or equal to the 90th percentile for low median household income as a percent of area median income and has low HS education in 2009 (island areas)? | `0` |
| IALMIL_76 | float | 118 | Low median household income as a percent of territory median income in 2009 (percentile) | `nan` |
| IAPLHS_77 | float | 114 | Percentage households below 100% of federal poverty line in 2009 for island areas (percentile) | `nan` |
| IAULHS_78 | float | 112 | Unemployment (percent) in 2009 for island areas (percentile) | `nan` |
| LHE | integer | 74,134 | Low high school education | `0` |
| IALHE | integer | 74,134 | Low high school education in 2009 (island areas) | `0` |
| IAHSEF | float | 117 | Percent individuals age 25 or over with less than high school degree in 2009 | `nan` |
| N_CLT_EOMI | integer | 74,134 | At least one climate threshold exceeded | `0` |
| N_ENY_EOMI | integer | 74,134 | At least one energy threshold exceeded | `0` |
| N_TRN_EOMI | integer | 74,134 | At least one traffic threshold exceeded | `0` |
| N_HSG_EOMI | integer | 74,134 | At least one housing threshold exceeded | `0` |
| N_PLN_EOMI | integer | 74,134 | At least one pollution threshold exceeded | `1` |
| N_WTR_EOMI | integer | 74,134 | At least one water threshold exceeded | `0` |
| N_HLTH_88 | integer | 74,134 | At least one health threshold exceeded | `1` |
| N_WKFC_89 | integer | 74,134 | At least one workforce threshold exceeded | `0` |
| FPL200S | integer | 74,134 | Is low income (imputed and adjusted)? | `0` |
| N_WKFC_91 | integer | 74,134 | Both workforce socioeconomic indicators exceeded | `0` |
| TD_ET | integer | 74,134 | Greater than or equal to the 90th percentile for DOT travel barriers | `0` |
| TD_PFS | float | 72,333 | DOT Travel Barriers Score (percentile) | `0.45` |
| FLD_PFS | float | 73,338 | Share of properties at risk of flood in 30 years (percentile) | `0.49` |
| WFR_PFS | float | 71,985 | Share of properties at risk of fire in 30 years (percentile) | `0.84` |
| FLD_ET | integer | 74,134 | Greater than or equal to the 90th percentile for share of properties at risk of flood in 30 years | `0` |
| WFR_ET | integer | 74,134 | Greater than or equal to the 90th percentile for share of properties at risk of fire in 30 years | `0` |
| ADJ_ET | integer | 74,134 | Is the tract surrounded by disadvantaged communities? | `0` |
| IS_PFS | float | 72,539 | Share of the tract's land area that is covered by impervious surface or cropland as a percent (percentile) | `0.26` |
| IS_ET | integer | 74,134 | Greater than or equal to the 90th percentile for share of the tract's land area that is covered by impervious surface or cropland as a percent | `0` |
| AML_ET | integer | 74,134 | Is there at least one abandoned mine in this census tract, where missing data is treated as False? | `0` |
| FUDS_RAW | string | 5,280 | Is there at least one Formerly Used Defense Site (FUDS) in the tract? | `None` |
| FUDS_ET | integer | 74,134 | Is there at least one Formerly Used Defense Site (FUDS) in the tract, where missing data is treated as False? | `0` |
| IMP_FLG | string | 73,976 | Income data has been estimated based on neighbor income | `0` |
| DM_B | float | 73,389 | Percent Black or African American | `0.96` |
| DM_AI | float | 73,302 | Percent American Indian / Alaska Native | `0.01` |
| DM_A | float | 73,391 | Percent Asian | `0` |
| DM_HI | float | 73,372 | Percent Native Hawaiian or Pacific | `0` |
| DM_T | float | 73,302 | Percent two or more races | `0` |
| DM_W | float | 73,390 | Percent White | `0.01` |
| DM_H | float | 73,387 | Percent Hispanic or Latino | `0` |
| DM_O | float | 73,382 | Percent other races | `0` |
| AGE_10 | float | 73,273 | Percent age under 10 | `0.13` |
| AGE_MIDDLE | float | 73,273 | Percent age 10 to 64 | `0.66` |
| AGE_OLD | float | 73,273 | Percent age over 64 | `0.2` |
| TA_COU_116 | float | 52 | Number of Tribal areas within Census tract for Alaska | `nan` |
| TA_COUNT_C | string | 0 | Number of Tribal areas within Census tract | `None` |
| TA_PERC | float | 2,156 | Percent of the Census tract that is within Tribal areas | `nan` |
| TA_PERC_FE | float | 2,156 | Percent of the Census tract that is within Tribal areas, for display | `nan` |
| UI_EXP | string | 74,134 | UI_EXP | `Nation` |
| THRHLD | integer | 74,134 | THRHLD | `21` |

## Low Income

### Low-Income Census Tracts

**NMTC_2016-2020_ACS_LIC_Sept1_2023.xlsb.** An Excel file of 2020 census tracts across the 50 U.S. states that includes an indicator for low-income. Published by the New Markets Tax Credit (NMTC) Program of the U.S. Department of the Treasury's Community Development Institutions Fund (CDIF). The U.S. Department of Energy (DOE), which administers the Low-Income Communities Bonus Credit Program under IRS tax code section 48(e), determines low-income eligibility using NMTC thresholds for low income. For more information, please consult the DOE's interactive mapping tool **[here](https://experience.arcgis.com/experience/12227d891a4d471497ac13f60fffd822)**.

**Metadata**

|  |  |
|---|---|
| Coordinate Reference System | N/A |
| Publisher | New Markets Tax Credit Program, Community Development Institutions Fund, U.S. Department of the Treasury  |
| Availability | May be downloaded directly from the fund's website **[here](https://www.cdfifund.gov/sites/cdfi/files/2023-08/NMTC_2016-2020_ACS_LIC_Sept1_2023.xlsb)**. |

**Fields**

_Sheet: 2016-2020_

| Field | Data Type | Non-Null Count | Description | Example |
|---|---|---|---|---|
| 2020 Census Tract Number FIPS code. GEOID | integer | 85395 | The Census Tract number is comprised of 11 digits, including a leading zero for states 01 through 09. The first two digits represent the state code. The next three digits represent the county code. And the remaining six digits represent the Census Tract code.  | `1001020100` |
| OMB Metro/Non-metro Designation, March 2020 (OMB Bulletin No. 20-01) | string | 85395 | A boolean variable indicating whether the census tract is a metropolitan area ("Metro") or non-metropolitan area ("Non-metro"). | `"Metro"` |
| Does Census Tract Qualify For NMTC Low-Income Community (LIC) on Poverty or Income Criteria? | string | 85395 | A boolean variable indicating whether the census tract qualifies as low-income under poverty or income criteria. Either "YES" or "NO". | `"NO"` |
| Census Tract Poverty Rate % (2016-2020 ACS) | float | 83812 | The current poverty rate, as listed in the 2016-2020 American Community Survey (ACS). | `13.7` |
| Does Census Tract Qualify on Poverty Criteria>=20%? | string | 85395 | A boolean variable indiating whether the census tract qualifies as low-income on the basis of poverty criteria. | `"NO"` |
| Census Tract Percent of Benchmarked Median Family Income (%) 2016-2020 ACS | float | 83037 | Median Family Income % is computed as follows: in the case of a tract not located within a metropolitan area,  the median family income for such tract does not exceed 80 percent of statewide median family income, or (ii) in the case of a tract located within a metropolitan area, the median family income for such tract does not exceed 80 percent of the greater of statewide median family income or the metropolitan area median family income. | `1.0379358437935844` |
| Does Census Tract Qualify on Median Family Income Criteria<=80%? | string | 85395 | A boolean variable indicating whether the census tract qualifies as low-income on the basis of median family income criteria. | `"NO"` |
| Census Tract Unemployment Rate (%) 2016-2020 | float | 85395 | The employment rate for the census tract as listed in the 2016-2020 American Community Survey. | `2.1` |
| County Code | integer | 85395 | The first five digits of the census tract number. | `01001` |
| State Name | string | 85395 | The name of the larger state. | `" Alabama"` |
| County Name | string | 85395 | The name of the larger county. | `" Autauga Caounty"` |
| Census Tract Unemployment to National Unemployment Ratio  | float | 85395 | The ratio between the census tract unemployment rate and the national unemployment rate, which is 5.4 percent. | `0.3888888955116272` |
| Is Tract Unemployment to National Unemployment Ratio >1.5? | string | 85395 | A boolean variable indicating whether the tract's unemployment rate is at least 1.5 times the national unemployment rate. Either "YES" or "NO". | `"NO"` |
| Population for whom poverty status is determined 2016-2020 ACS | integer | 85395 | The subset of the total population for whom poverty status was calculated. Excludes institutionalized persons, persons living on military bases, persons in college dormitories, and unrelated individuals under 15 years old. | `1941` |

_Sheet: High migration tracts_

| Field | Data Type | Non-Null Count | Description | Example |
|---|---|---|---|---|
| 2020 Census Tract Number FIPS code. GEOID | string | 62 | The Census Tract number is comprised of 11 digits, including a leading zero for states 01 through 09. The first two digits represent the state code. The next three digits represent the county code. And the remaining six digits represent the Census Tract code.  | `"01035960400"` |
| High migration nonmetro county 20 year population loss, 2020-2010 | string | 62 | The percentage of population decline in the larger county from 2010 to 2020. | `"-12.3%"` |
| Census Tract Percent of Benchmarked Median Family Income (%) 2016-2020 ACS | string | 62 | The median family income in the census tract as a percentage of the median family income in the applicable geographic area. | `"82%"` |


**NMTC_LIC_Territory_2020_December_2023.xlsx.** An Excel file of 2020 census tracts across the six major island territories (i.e., American Samoa, Guam, the Commonwealth of the Northern Mariana, Puerto Rico, and the U.S. Virgin Islands) that includes a low-income indicator. Completed and published separately by NMTC after the above file, `NMTC_2016-2020_ACS_LIC_Sept1_2023.xlsb`, had already been released.

**Metadata**

|  |  |
|---|---|
| Coordinate Reference System | N/A |
| Publisher | New Markets Tax Credit Program, Community Development Institutions Fund, U.S. Department of the Treasury  |
| Availability | May be downloaded directly from the fund's website **[here](https://www.cdfifund.gov/sites/cdfi/files/2023-12/NMTC_LIC_Territory_2020_December_2023.xlsx)**. |

**Fields**

_Sheet: NMTC LIC 2020_

| Field | Data Type | Non-Null Count | Description | Example |
|---|---|---|---|---|
| 2020 Census Tract Number FIPS code. GEOID | integer | 133 | The Census Tract number is comprised of 11 digits, including a leading zero for states 01 through 09. The first two digits represent the state code. The next three digits represent the county code. And the remaining six digits represent the Census Tract code.  | `66010950502` |
| OMB Metro/Non-metro Designation, March 2020 (OMB Bulletin No. 20-01) | string | 133 | A boolean variable indicating whether the census tract is a metropolitan area ("Metro") or non-metropolitan area ("Non-metro"). | `"Non-Metro"` |
| Does Census Tract Qualify For NMTC Low-Income Community (LIC) on Poverty or Income Criteria? | string | 133 | A boolean variable indicating whether the census tract qualifies as low-income under poverty or income criteria. Either "YES" or "NO". | `"YES"` |
| Census Tract Poverty Rate % (2020 Island Areas) | string | 111 | The current poverty rate, as listed in the 2020 Island Areas Survey. | `"56.4%"` |
| Does Census Tract Qualify on Poverty Criteria>=20%? | string | 133 | A boolean variable indiating whether the census tract qualifies as low-income on the basis of poverty criteria. | `"YES"` |
| Census Tract Percent of Benchmarked Median Family Income (%) 2020 Island Areas | string | 110 | Median Family Income % is computed as follows: in the case of a tract not located within a metropolitan area,  the median family income for such tract does not exceed 80 percent of statewide median family income, or (ii) in the case of a tract located within a metropolitan area, the median family income for such tract does not exceed 80 percent of the greater of statewide median family income or the metropolitan area median family income. | `"83.8%"` |
| Does Census Tract Qualify on Median Family Income Criteria<=80%? | string | 133 | A boolean variable indicating whether the census tract qualifies as low-income on the basis of median family income criteria. | `"NO"` |
| Census Tract Unemployment Rate (%) 2016-2020 | float | 111 | The employment rate for the census tract as listed in the 2020 Island Areas Survey. | `"15%"` |
| County Code | integer | 133 | The first five digits of the census tract number. | `60010` |
| State Name | string | 133 | The name of the larger state. | `"American Samoa"` |
| County Name | string | 133 | The name of the larger county. | `"Eastern District"` |
| Census Tract Unemployment to National Unemployment Ratio  | float | 111 | The unemployment rate ratio is the ratio between the census tract unemployment rate and the national unemployment rate, which is 5.4 percent. | `10.44` |
| Is Tract Unemployment to National Unemployment Ratio >1.5? | string | 111 | A boolean variable indicating whether the tract's unemployment rate is at least 1.5 times the national unemployment rate. Either "YES" or "NO". | `"YES"` |
| Population | integer | 133 | The census tract population. | `2545` |