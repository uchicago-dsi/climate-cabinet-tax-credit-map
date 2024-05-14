# Overview

## About

**The Tax Credit Bonus Map Widget is a full-stack web application allowing local officials to search for tax credit bonuses newly-available under the Inflation Reduction Act (2020) within their state, county, municipality, municipal utility, or rural cooperative.** It launched in February 2024 following a collaboration between **[Climate Cabinet Education](https://climatecabineteducation.org/)** and the **[University of Chicago Data Science Institute](https://11thhourproject.org/)**, with generous support from the **[11th Hour Project](https://11thhourproject.org/)**.

At the time of writing, the app's featured tax credit programs include the Alternative Fuel Refueling Property Credit, Clean Electricity Investment Tax Credit, Clean Electricity Production Tax Credit, Neighborhood Access and Equity Grant, and Solar for All. Program eligibilty is determined by the presence of a low-income, distressed, energy, and/or Justice 40 community within the jurisdiction, and tax credits can stack if a jurisdiction contains more than one of these "bonus" communities.

## Use Case

The application is not intended to be a standalone website, but a "widget" embedded as an HTML iframe in Climate Cabinet Education's main WordPress site. During the development proces, decoupling the widget from the site permitted more safety and flexibility. Because the widget's logic and configuration could be updated independently, software engineers external to Climate Cabinet never required elevated permissions or access to the organization's core code bases. In addition, engineers were able to take advantage of popular JavaScript libraries when designing the front-end rather than work within the system of WordPress plugins.

## Features

Users can currently:

- Search for a geography by name by typing into an autocomplete box. After a configured debounce period, they will see a dropdown of search results or "No Results Found" based on their search phrase.

- Click on a search result and wait for the web app to process their request. Upon completion, the map zooms to the boundaries of the selected geography and shows the current geography and all of its bonus communities as Mapbox tileset layers. In addition, a summary of the geography, its bonus communities, and eligible programs, along with population counts, are displayed in the sidebar.

- Hover over geographies on the map to view their names.

- Select which tileset layer(s) to view at once by toggling checkboxes in the map control panel.

- Switch between political and satellite base maps using radio buttons in the map control panel.

- Open a full-screen view of the map by clicking on the expand button in the map's upper lefthand corner.

## Future Improvements

- Federally Recognized Tribal Lands, including Alaska Native Villages, are not yet included in the application, but those areas are eligible for IRA tax credits on the basis of qualifying as low-income and Justice40 communities.

- Data dictionaries have not yet been completed for all datasets listed in the documentation.