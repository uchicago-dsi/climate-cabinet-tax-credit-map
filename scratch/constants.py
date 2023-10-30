"""Constants used throughout the application.
"""

from pathlib import Path

# Directories
ROOT_DIR = Path(__file__).parent
DATA_DIR = ROOT_DIR / "data"
CLEAN_DATA_DIR = DATA_DIR / "clean"
GEOPARQUET_DIR = CLEAN_DATA_DIR / "geoparquet"
GEOJSONL_DIR = CLEAN_DATA_DIR / "geojsonl"
RAW_DATA_DIR = DATA_DIR / "raw"

# State abbreviations
STATE_ABBREVIATIONS = {
    
    # 50 states
    'AK': 'Alaska',
    'AL': 'Alabama',
    'AR': 'Arkansas',
    'AZ': 'Arizona',
    'CA': 'California',
    'CO': 'Colorado',
    'CT': 'Connecticut',
    'DE': 'Delaware',
    'FL': 'Florida',
    'GA': 'Georgia',
    'HI': 'Hawaii',
    'IA': 'Iowa',
    'ID': 'Idaho',
    'IL': 'Illinois',
    'IN': 'Indiana',
    'KS': 'Kansas',
    'KY': 'Kentucky',
    'LA': 'Louisiana',
    'MA': 'Massachusetts',
    'MD': 'Maryland',
    'ME': 'Maine',
    'MI': 'Michigan',
    'MN': 'Minnesota',
    'MO': 'Missouri',
    'MS': 'Mississippi',
    'MT': 'Montana',
    'NC': 'North Carolina',
    'ND': 'North Dakota',
    'NE': 'Nebraska',
    'NH': 'New Hampshire',
    'NJ': 'New Jersey',
    'NM': 'New Mexico',
    'NV': 'Nevada',
    'NY': 'New York',
    'OH': 'Ohio',
    'OK': 'Oklahoma',
    'OR': 'Oregon',
    'PA': 'Pennsylvania',
    'RI': 'Rhode Island',
    'SC': 'South Carolina',
    'SD': 'South Dakota',
    'TN': 'Tennessee',
    'TX': 'Texas',
    'UT': 'Utah',
    'VA': 'Virginia',
    'VT': 'Vermont',
    'WA': 'Washington',
    'WI': 'Wisconsin',
    'WV': 'West Virginia',
    'WY': 'Wyoming',

    # District of Columbia
    'DC': 'District of Columbia',

    # U.S. Territories
    'AS': 'American Samoa',
    'PR': 'Puerto Rico',
    'GU': 'Guam',
    'MP': 'Northeren Mariana Islands',
    'VI': 'Virgin Islands'
}
