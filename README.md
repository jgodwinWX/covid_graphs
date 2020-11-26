# COVID Graphs

covid_plotter.py: This script pulls data from the [COVID Tracking Project](https://covidtracking.com/data/download), but
this will be deprecated soon and needs to be changed to the API. After the data is imported, various graphs are created.

countymaps.py: This script pulls data from the [New York Times GitHub](https://github.com/nytimes/covid-19-data/)
then uses a state population CSV (included here as fipscodes.csv) to compute and then map the cases per one million
residents for each county, with a different map for each state.

webgen.py: This script creates some basic HTML that can be pasted into a webpage [such as the one on my website](http://jasonsweathercenter.com/covid.html).
