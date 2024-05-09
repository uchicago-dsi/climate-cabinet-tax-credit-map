# Raw Datasets

The application stores datasets that were either compiled by hand or manually downloaded from external sources without modification in file storage under `data/raw`. The folder is structured as follows:

```
├── raw/
│   ├── bonus/
│   │   ├── distressed/
│   │   ├── energy/
│   │   ├── justice40/
│   │   └── low_income/
│   ├── census/
│   │   ├── block_groups/
│   │   ├── blocks/
│   │   ├── counties/
│   │   ├── county_subdivisions/
│   │   ├── government_units/
│   │   ├── places/
│   │   ├── states/
│   │   ├── tracts/
│   │   └── zip_codes/
│   └── retail/
```

These datasets serve as inputs to the pipeline; they are cleaned and standardized, and the resulting output is used to populate the `tax_credit_geography` table. Broadly, they fall into three categories: (1) target geographies, (2) bonus geographies, or (3) population counts.

## Target Geographies

The application stores five different types of "target geographies" (i.e., geographies available for user search) in the database:

1. States
2. Counties
3. Municipalities
4. Municipal Utilities
5. Rural Cooperatives

Geographic boundaries and metadata for states and counties were sourced directly from U.S. Census Bureau shapefiles. Municipalities were identified by merging the Census Bureau's census of government units with its place and county subdivision shapefiles. Boundaries for municipal utilities and rural cooperatives were sourced directly from the Department of Homeland Security. Finally, Climate Cabinet provided a list of common/standard names for utilities and select municipalities that was used to update the datasets.

## Bonus Geographies

The application stores four different types of tax credit bonus communities within the database. These communities are eligible for the Neighborhood Access and Equity Grant Program, Solar for All Program, Alternative Fuel Refueling Property Credit, and/or the Direct Pay Clean Energy Investment and Production Tax Credits. 

### Distressed Communities

Since 2015, the bipartisan public policy think tank **[Economic Innovation Group (EIG)](https://eig.org/)** has used American Community Survey 5-Year Estimates and Census Business Patterns datasets to publish a Distressed Community Index (DCI). The index evaluates zip code tabulation areas (ZCTAs), counties, and congressional districts along seven equally-weighted dimensions:

1. Share of the population 25 years of age and older without a high school diploma
2. Housing vacancy rate
3. Share of the prime-age working population aged 25 to 54 who are not currently employed
4. Poverty rate
5. Median household income as a share of metro or state area median household income
6. Percent change in jobs over the last five years
7. Percent change in the number of business establishments over the last five years.

Each ZCTA, county, and congressional district is assigned a rank for each dimension; its ranks are then averaged to create a preliminary score. For each geography type, the preliminary scores are normalized into a final "Distress Score" ranging from 0 (most prosperous) to 100 (most distressed). Finally, the Distress Scores are separated into five quintiles of well-being: prosperous, comfortable, mid-tier, at risk, and distressed.

According to Climate Cabinet, communities identified as distressed are eligible to apply for grants through the U.S. Department of Transportation's **[Neighborhood Access and Equity Grant Program](https://www.transportation.gov/grants/rcnprogram/about-neighborhood-access-and-equity-grant-program)** and the U.S. Environmental Protection Agency's **[Solar for All Program](https://www.epa.gov/greenhouse-gas-reduction-fund/solar-all)**. **The application uses distressed ZCTAs as distressed communities and merges them with ZCTA Shapefiles provided by the U.S. Census Bureau to produce the geographies saved in the database.**

### Energy Communities

The Inflation Reduction Act (IRA) **[defines an energy community](https://energycommunities.gov/energy-community-tax-credit-bonus/)** as a geography that satisfies one of the following criteria:

- A "brownfield site," as defined in certain subparagraphs of the Comprehensive Environmental Response, Compensation, and Liability Act of 1980 (CERCLA).

- A "metropolitan statistical area" (MSA) or "non-metropolitan statistical area" (non-MSA) that has (or had at any time after 2009) 0.17 percent or greater direct employment or 25 percent or greater local tax revenues related to the extraction, processing, transport, or storage of coal, oil, or natural gas; and has an unemployment rate at or above the national average unemployment rate for the previous year.

- A census tract (or directly adjoining census tract) in which a coal mine has closed after 1999; or in which a coal-fired electric generating unit has been retired after 2009.

Local officials who build and operate projects, facilities, or technologies within these energy communities are eligible to receive the Energy Community Tax Credit Bonus: i.e., up to a 10 percent bonus for the **[Clean Electricity Production Tax Credit](https://energycommunities.gov/funding-opportunity/clean-electricity-production-tax-credit-26-u-s-code-%C2%A4-45y/)** or up to 10 percentage points for the **[Clean Electricity Investment Tax Credit](https://energycommunities.gov/funding-opportunity/clean-electricity-investment-tax-credit-26-u-s-code-%C2%A4-48e/)**, both of which are available through **[direct pay](https://www.whitehouse.gov/cleanenergy/directpay/)**.

**The application sources energy community boundaries from the Interagency Working Group on Coal and Power Plant Communities and Economic Revitalization** based in the U.S. Department of Energy's National Energy Technology Laboratory. At the time of writing, locations for brownfield sites have not yet been released.

### Justice 40 Communities

The Biden-Harris administration's Justice40 Initiative, issued in 2021 through an executive order, is a government effort to ensure that at least 40 percent of certain federal climate, clean energy, and affordable and sustainable housing investments, among others, flow to the disadvantaged communities most affected by poverty and legacy pollution. To identify these communities, a new division of the Executive Office of the President, the Council on Environmental Quality (CEQ), created **[eight categories of burdens](https://screeningtool.geoplatform.gov/en/methodology)**:

1. **Climate Change.** Communities at or above the 90th percentile for the expected agriculture loss rate OR expected building loss rate OR expected population loss rate OR projected flood risk OR projected wildfire risk AND at the 65th percentile or above for low income.

2. **Energy.** Communities at or above the 90th percentile for energy cost OR PM2.5 in the air AND at the 65th percentile or above for low income.

3. **Health.** Communities at or above the 90th percentile for asthma OR diabetes OR heart disease OR low life exepctancy AND at the 65th percentile or above for low income.

4. **Housing.** Communities that experienced historic underinvestment OR are at or above the 90th percentile for housing cost OR lack of green space OR lack of indoor plumbing OR lead paint AND are at the 65th percentile or above for low income.

5. **Legacy Pollution.** Communities that have at least one abandoned mine land OR Formerly Used Defense Sites OR are at or above the 90th percentile for proximity to hazardous waste facilities OR proximity to Superfund sites (National Priorities List, or NPL) OR proximity to Risk Management Plan (RMP) facilities AND are at the 65th percentile or above for low income.

6. **Transportation.** Communities at or above the 90th percentile for diesel particulate matter exposure OR transportation barriers OR traffic proximity and volume AND at or above the 65th percentile for low income.

7. **Water and Wastewater.** Communities at or above the 90th percentile for underground storage tanks and releases OR wastewater discharge AND are at or above the 65th percentile for low income.

8. **Workforce Development.** Communities at or above the 90th percentile for linguistic isolation OR low median income OR poverty OR unemployment AND having more than 10 percent of people ages 25 years or older with less than a high school diploma.

Census tracts (2010) across the 50 states, the District of Columbia, and the U.S. territories that meet any of these criteria are considered disadvantaged. In addition, all Federally Recognized Tribes, including Alaska Native Villages, are automatically considered disadvantaged. **The application uses the Justice40 boundaries available for direct download through the CEQ's Climate and Economic Justice Screening Tool.** Justice40 tracts are eligible for the U.S. Environmental Protection Agency's **[Solar for All Program](https://www.epa.gov/greenhouse-gas-reduction-fund/solar-all)**

### Low-Income Communities

The U.S. Department of Energy (DOE), which administers the **[Low-Income Communities Bonus Credit Program](https://www.energy.gov/justice/low-income-communities-bonus-credit-program)** under IRS tax code section 48(e), determines low-income eligibility using the New Markets Tax Credit (NMTC) Program's thresholds for low income. The NMTC program is run by the U.S. Department of the Treasury's Community Development Institutions Fund (CDIF) and under **[statute (26 USC §45D(e))](http://cdfifund.gov/docs/2000_nmtc_statute.pdf)** and amendments from the American Jobs Creation Act of 2004 (P.L. 108-357, 118 Stat. 1418), defines low-income communities as follows:

1. Census tracts with a poverty rate of 20 percent or greater,
2. Census tracts with a median family income at or below 80 percent of the applicable area median family income, OR
3. Census tracts in a High Migration Rural County with a median family income at or below 85 percent of the applicable area median family income

A High Migration Rural County is any county with a 10 percent or greater population drop in the 20 years preceding the latest census. When any tract is located outside a metropolitian statistical area, its point of comparision is state median family income. Otherwise, the point of comparision is the greater of the state or metropolitan area median family income.

Low-income communities are eligible for the **[Alternative Fuel Vehicle Refueling Property Credit](https://www.anl.gov/esia/refueling-infrastructure-tax-credit)**, the U.S. Environmental Protection Agency's **[Solar for All Program](https://www.epa.gov/greenhouse-gas-reduction-fund/solar-all)**, and the U.S. Department of the Treasury's **[Clean Electricity Production Tax Credit](https://energycommunities.gov/funding-opportunity/clean-electricity-production-tax-credit-26-u-s-code-%C2%A4-45y/)** and **[Clean Electricity Investment Tax Credit](https://energycommunities.gov/funding-opportunity/clean-electricity-investment-tax-credit-26-u-s-code-%C2%A4-48e/)**. **The application merges the latest list of NMTC low-income census tracts with 2020 census tract Shapefiles from the U.S. Census Bureau to produce the geographies saved in the database.** 

## Population Counts

The application adds population counts to each geography in the database to give users a sense of how many persons could be affected by an infrastructure or investment project. These counts are pulled directly from the 2020 U.S. census if the geography uses 2020 census boundaries. However, if the geography references older census boundaries; is not related to the census at all, as in the case of municipal utilities and rural cooperatives; or is a spatial intersection between two geographies that lacks a FIPS code, population is estimated by summing block-group level population-weighted centroids that fall within the geography.

The U.S. Census Bureau provides these centroids for the 50 states, the District of Columbia, and Puerto Rico. To allow population estimates for the remaining U.S. Island Areas (i.e., American Samoa, the Commonwealth of the Northern Mariana Islands, Guam, and the U.S. Virgin Islands), the application creates block group centroids using block-level housing counts.