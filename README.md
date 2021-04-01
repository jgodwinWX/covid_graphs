# COVID Graphs

April 01, 2021 Update:

The code is back up and running! Data is now being pulled from the APIs from the CDC and HHS (see below).

March 30, 2021 Update:

As of early March, the COVID Tracking Project has ended. This script is now using APIs from the Centers for Disease Control 
and U.S. Department of Health and Human Services. The old code that used COVID Tracking Project is now in the v1 folder for 
posterity, but this code will no longer pull in the latest data. The following APIs are used:
- Cases and Deaths: [CDC U.S. COVID-19 Cases and Deaths by State over Time](https://data.cdc.gov/Case-Surveillance/United-States-COVID-19-Cases-and-Deaths-by-State-o/9mfq-cb36).
- Excess Mortality (new!): [NCHS Excess Deaths Associated with COVID-19](https://data.cdc.gov/NCHS/Excess-Deaths-Associated-with-COVID-19/xkkf-xrst).
- Hospitalizations: [HHS COVID-19 Reported Patient Impact and Hospital Capacity by State Timeseries](https://healthdata.gov/Hospital/COVID-19-Reported-Patient-Impact-and-Hospital-Capa/g62h-syeh).

covid_plotter.py: This script pulls data from the APIs listed above. After the data is imported, various charts are created.

countymaps.py: This script pulls data from the [New York Times GitHub](https://github.com/nytimes/covid-19-data/)
then uses a state population CSV (included here as fipscodes.csv) to compute and then map the cases per one million
residents for each county, with a different map for each state. This uses a different data source that is still being updated and should be okay.

webgen.py: This script creates some basic HTML that can be pasted into a webpage [such as the one on my website](http://jasonsweathercenter.com/covid.html).
