import pandas as pd
import numpy as np
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib as mpl
import datetime

# view all rows for troubleshooting purposes
pd.set_option('display.max_rows',None)

# list of states and names
states = ['01','02','04','05','06','08','09','10','12','13','15','16','17','18','19','20','21',\
    '22','23','24','25','26','27','28','29','30','31','32','33','34','35','36','37','38','39',\
    '40','41','42','44','45','46','47','48','49','50','51','53','54','55','56']
statenames = ['Alabama','Alaska','Arizona','Arkansas','California','Colorado','Connecticut',\
    'Delaware','Florida','Georgia','Hawaii','Idaho','Illinois','Indiana','Iowa','Kansas',\
    'Kentucky','Louisiana','Maine','Maryland','Massachusetts','Michigan','Minnesota',\
    'Mississippi','Missouri','Montana','Nebraska','Nevada','New Hampshire','New Jersey',\
    'New Mexico','New York','North Carolina','North Dakota','Ohio','Oklahoma','Oregon',\
    'Pennsylvania','Rhode Island','South Carolina','South Dakota','Tennessee','Texas','Utah',\
    'Vermont','Virginia','Washington','West Virginia','Wisconsin','Wyoming']
    
# load the shapefile data
fp = '/home/jgodwin/python/covid/gis/cb_2018_us_county_500k.shp'
map_df = gpd.read_file(fp)
covid_data = pd.read_csv('https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties.csv',dtype={'fips':'str'})

# compute the weekly cases
today = covid_data['date'].values[-1]
today_dt = datetime.datetime.strptime(today,'%Y-%m-%d')
week_dt = today_dt - datetime.timedelta(days=7)
weekago = datetime.datetime.strftime(week_dt,'%Y-%m-%d')
latest_data = covid_data[covid_data['date']==today]
weekago_data = covid_data[covid_data['date']==weekago]
weekly_data = latest_data.merge(weekago_data,how='left',left_on='fips',right_on='fips')
weekly_data['weekcases'] = weekly_data['cases_x'] - weekly_data['cases_y']

for ix,state in enumerate(states):
    print(statenames[ix])
    # get the state GIS data
    state_df = map_df[map_df['STATEFP']==state]

    # remove Aleutians West to avoid crossing hemispheres
    if state == '02':
        state_df = state_df[state_df['GEOID']!='02016']
        weekly_data = weekly_data[weekly_data['fips']!='02016']

    # clean up New York data
    if state != '36':
        continue

    # join the two dataframes
    merged_df = state_df.merge(weekly_data,how='left',left_on='GEOID',right_on='fips')
    merged_df = merged_df.fillna(0)

    #print(merged_df.loc[merged_df['weekcases'].idxmax()]['NAME'],merged_df.loc[merged_df['weekcases'].idxmax()]['weekcases'])

    # create the colorbar
    plt.clf()
    cmap = plt.cm.jet
    cmaplist = [cmap(i) for i in range(cmap.N)]
    cmaplist[0] = (0.5,0.5,0.5,1.0)
    cmap = mpl.colors.LinearSegmentedColormap.from_list('Custom cmap',cmaplist,cmap.N)
    bounds = [0,1,5,10,50,100,500,1000,5000,10000,50000,100000]
    norm = mpl.colors.BoundaryNorm(bounds,cmap.N)

    # create the plot
    plt.clf()
    variable = 'weekcases'
    fig,ax = plt.subplots(1,figsize=(24,12))
    ax.axis('off')
    ax.set_title('COVID-19 Cases in Last 7 Days in %s (data as of %s)' % (statenames[ix],today))
    merged_df.plot(column=variable,cmap=cmap,norm=norm,linewidth=0.8,ax=ax,edgecolor='black')

    # plot the colorbar
    ax2 = fig.add_axes([0.95,0.1,0.03,0.8])
    cb = mpl.colorbar.ColorbarBase(ax2,cmap=cmap,norm=norm,spacing='uniform',ticks=bounds,boundaries=bounds,format='%1i')

    # make a basic plot
    plt.savefig('/var/www/html/images/covid/countymaps/cases_%s.png' % state,bbox_inches='tight')
    plt.close('all')
    if state == '36':
        break
print('Done.')
