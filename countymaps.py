import csv
import pandas as pd
import numpy as np
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.dates as mdates
import matplotlib.ticker as mtick
import datetime
import seaborn

def trends(data,pct=False):
    # we just want the percentage point change for the positivity change
    if pct:
        trendweek = data[-1] - data[-8]
        trend2week = data[-1] - data[-15]
        trendmonth = data[-1] - data[-31]
    else:
        trendweek = (data[-1] - data[-8]) / data[-8]
        trend2week = (data[-1] - data[-15]) / data[-15]
        trendmonth = (data[-1] - data[-31]) / data[-31]
    return(data[-1],data[-8],data[-15],data[-31],trendweek,trend2week,trendmonth)

# function for writing CSVs for trend data
def makeCSV(filename,data):
    with open(filename,'w',encoding='UTF8',newline='') as f:
        writer = csv.writer(f)
        writer.writerows(data)
        f.close()

# window to view data (i.e. past x days)
window = 180

# debugging options
#pd.set_option('display.max_rows',50)
debug = False
plotcounties = True 
statemaps = True 
metroplots = True

# list of states and names
states = ['01','02','04','05','06','08','09','10','12','13','15','16','17','18','19','20','21',
    '22','23','24','25','26','27','28','29','30','31','32','33','34','35','36','37','38','39',
    '40','41','42','44','45','46','47','48','49','50','51','53','54','55','56']
statenames = ['Alabama','Alaska','Arizona','Arkansas','California','Colorado','Connecticut',
    'Delaware','Florida','Georgia','Hawaii','Idaho','Illinois','Indiana','Iowa','Kansas',
    'Kentucky','Louisiana','Maine','Maryland','Massachusetts','Michigan','Minnesota',
    'Mississippi','Missouri','Montana','Nebraska','Nevada','New Hampshire','New Jersey',
    'New Mexico','New York','North Carolina','North Dakota','Ohio','Oklahoma','Oregon',
    'Pennsylvania','Rhode Island','South Carolina','South Dakota','Tennessee','Texas','Utah',
    'Vermont','Virginia','Washington','West Virginia','Wisconsin','Wyoming']
metrodict = {'New York/Tri-State':['09001','09005','09009','34003','34013','34017','34019',
    '34021','34023','34025','34027','34029','34031','34035','34037','34039','36005','36027',
    '36047','36059','36061','36071','36079','36081','36085','36087','36103','36111','36119',
    '42089','42103'],
    'Greater Los Angeles':['06037','06059','06065','06071','06111'],
    'Chicagoland':['17031','17037','17043','17063','17089','17091','17093','17097','17111','17197',
        '18073','18089','18111','18127','55059'],
    'Baltimore/Washington Metropolitan Area':['11001','24003','24510','24005','24009','24013',
        '24017','24021','24025','24027','24031','24033','24035','24037','24041','24043','42055',
        '51510','51013','51043','51047','51600','51059','51610','51061','51069','51630','51107',
        '51683','51685','51153','51157','51177','51179','51187','51840','54003','54027','54037'],
    'San Francisco Bay Area':['06001','06013','06041','06055','06075','06081','06085','06095',
        '06097'],\
    'Greater Boston':['09015','25001','25005','25009','25017','25021','25023','25025','25027',
        '33017','33015','33001','33011','33013','44001','44003','44005','44007','44009'],
    'Dallas/Fort Worth Metroplex':['40013','48085','48097','48113','48121','48139','48147','48181',
        '48213','48221','48231','48251','48257','48349','48363','48367','48397','48439','48497'],
    'Greater Houston':['48015','48039','48071','48157','48167','48201','48291','48321','48339',
        '48471','48473','48477','48481'],
    'Philadelphia/Delaware Valley':['10001','10003','24015','34001','34005','34007','34009',
        '34011','34015','34033','42011','42017','42029','45045','42091','42101'],
    'Greater Miami':['12011','12061','12085','12086','12099','12111'],
    'Greater Oklahoma City':['40017','40027','40051','40081','40083','40087','40109','40125']
    }
metroabbv = {'New York/Tri-State':'nyc','Greater Los Angeles':'lax','Chicagoland':'chi',
    'Baltimore/Washington Metropolitan Area':'bwi','San Francisco Bay Area':'sfo',
    'Greater Boston':'bos','Dallas/Fort Worth Metroplex':'dfw','Greater Houston':'hou',
    'Philadelphia/Delaware Valley':'phi','Greater Miami':'mia','Greater Oklahoma City':'okc'}
    
# load the shapefile data
fp = '/home/jgodwin/python/covid/gis/cb_2018_us_county_500k.shp'
map_df = gpd.read_file(fp)
covid_data = pd.read_csv('https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties.csv',dtype={'fips':'str'})
population_data = pd.read_csv('/home/jgodwin/python/covid/fipscodes.csv',dtype={'fips':'str'})

# compute the weekly cases
today = covid_data['date'].values[-1]
print(today)
today_dt = datetime.datetime.strptime(today,'%Y-%m-%d')
week_dt = today_dt - datetime.timedelta(days=7)
weekago = datetime.datetime.strftime(week_dt,'%Y-%m-%d')
latest_data = covid_data[covid_data['date']==today]
weekago_data = covid_data[covid_data['date']==weekago]
weekly_data = latest_data.merge(weekago_data,how='left',left_on='fips',right_on='fips')
weekly_data['weekcases'] = weekly_data['cases_x'] - weekly_data['cases_y']

if statemaps:
    for ix,state in enumerate(states):
        if debug and state != '22':
            continue
        print(statenames[ix])
        # get the state GIS data
        state_df = map_df[map_df['STATEFP']==state]

        # remove Aleutians West to avoid crossing hemispheres
        if state == '02':
            state_df = state_df[state_df['GEOID']!='02016']
            weekly_data = weekly_data[weekly_data['fips']!='02016']

        # join the two dataframes
        merged_df = state_df.merge(weekly_data,how='left',left_on='GEOID',right_on='fips')
        # merge the data dataframe with the population dataframe
        merged_df = merged_df.merge(population_data,how='left',left_on='GEOID',right_on='fips')
        merged_df = merged_df.fillna(0)
        
        # compute cases per 1M people
        merged_df['casesPer1M'] = merged_df['weekcases'] / (merged_df['Population']/1E6)

        # create the colorbar
        plt.clf()
        cmap = plt.cm.jet
        cmaplist = [cmap(i) for i in range(cmap.N)]
        cmaplist[0] = (0.5,0.5,0.5,1.0)
        cmap = mpl.colors.LinearSegmentedColormap.from_list('Custom cmap',cmaplist,cmap.N)
        bounds = [0,10,50,100,500,1000,2000,4000,6000,8000,10000,20000]
        norm = mpl.colors.BoundaryNorm(bounds,cmap.N)

        # create the plot
        plt.clf()
        variable = 'casesPer1M'
        fig,ax = plt.subplots(1,figsize=(24,12))
        ax.axis('off')
        ax.set_title('COVID-19 Cases per 1M people in Last 7 Days in %s (data as of %s)' % (statenames[ix],today))
        merged_df.plot(column=variable,cmap=cmap,norm=norm,linewidth=0.8,ax=ax,edgecolor='black')

        # plot the colorbar
        ax2 = fig.add_axes([0.95,0.1,0.03,0.8])
        cb = mpl.colorbar.ColorbarBase(ax2,cmap=cmap,norm=norm,spacing='uniform',ticks=bounds,boundaries=bounds,format='%1i')

        # make a basic plot
        plt.savefig('/var/www/html/images/covid/countymaps/cases_%s.png' % state,bbox_inches='tight')
        plt.close('all')

        if debug and state=='22':
            break

# plot some counties of interest
if plotcounties:
    county_code = ['22055','48439','48201','06085','48085','48113','48121','22005','22033','04013',\
        '06037','12086','12011','22071']
    county_name = ['Lafayette, LA','Tarrant, TX','Harris, TX','Santa Clara, CA','Collin, TX',\
        'Dallas, TX','Denton, TX','Ascension, LA','East Baton Rouge, LA','Maricopa, AZ',\
        'Los Angeles, CA','Miami-Dade, FL','Broward, FL','Orleans, LA']
    for j,code in enumerate(county_code):
        # get the county level case data
        dataset = covid_data[covid_data['fips'] == code]
        dataset['date'] = pd.to_datetime(dataset['date'],format='%Y-%m-%d')
        dataset['dailycases'] = dataset['cases'].diff()
        dataset['dailycases'].mask(dataset['dailycases'] < 0,inplace=True)
        dataset['weeklycases'] = dataset['dailycases'].rolling(window=7).mean()
        fig,ax = plt.subplots(figsize=(12,8))
        ax.bar(dataset['date'][-window:],dataset['dailycases'][-window:],color='blue',label='Daily Cases')
        ax.plot(dataset['date'][-window:],dataset['weeklycases'][-window:],marker='o',markevery=[-1],color='red',label='7-Day Moving Average')
        plt.text(dataset['date'].values[-1],dataset['weeklycases'].values[-1],'{0:,.0f}'.format(dataset['weeklycases'].values[-1]),color='red')
        plt.grid(which='major',axis='x',linestyle='-',linewidth=2)
        plt.grid(which='minor',axis='x',linestyle='--')
        plt.grid(which='major',axis='y',linestyle='-')
        plt.title('Daily COVID-19 Cases in County: %s\n(latest data: %s)' % (county_name[j],today))
        plt.xlabel('Date')
        ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x,p: format(int(x),',')))
        ax.set_ylabel('Confirmed Cases')
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d/%y'))
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        ax.xaxis.set_minor_locator(mdates.DayLocator(bymonthday=(1,8,15,22)))
        plt.legend(loc='upper right')
        plt.savefig('/var/www/html/images/covid/%s.png' % code,bbox_inches='tight')
        plt.close(fig)

# metropolitan areas
if metroplots:
    case_trend = [['metro area','new cases','one week ago','two weeks ago','30 days ago',\
        '7-day trend','14-day trend','30-day trend']]
    for i in metrodict.keys():
        if debug:
            i = list(metrodict.keys())[-1]
        print('Metropolitan Area: %s' % i)
        # since NYC is not broken down into its five counties, we need to grab New York City itself
        if i == 'New York/Tri-State':
            metrodata = covid_data[covid_data['fips'].isin(metrodict['New York/Tri-State'])]\
                .groupby('date').sum().diff() + covid_data[covid_data['county']=='New York City']\
                .groupby('date').sum().diff()
        else:
            metrodata = covid_data[covid_data['fips'].isin(metrodict[i])].groupby('date').sum().diff()
        metrodata.index = pd.to_datetime(metrodata.index)
        fig,ax = plt.subplots(figsize=(12,8))
        ax.bar(metrodata.index[-window:],metrodata['cases'][-window:],color='blue',\
            label='Daily Cases')
        ax.plot(metrodata.index[-window:],metrodata['cases'][-window:].rolling(window=7).mean(),\
            color='red',label='7-Day Moving Average',marker='o',markevery=[-1])
        plt.text(metrodata.index[-1],metrodata['cases'][-window:].rolling(window=7).mean()[-1],\
            '{0:,.0f}'.format(metrodata['cases'][-window:].rolling(window=7).mean()[-1]),\
            color='red')
        plt.grid(which='major',axis='x',linestyle='-',linewidth=2)
        plt.grid(which='minor',axis='x',linestyle='--')
        plt.grid(which='major',axis='y',linestyle='-')
        plt.title('Daily COVID-19 Cases in %s\n(latest data: %s)' % (i,metrodata.index[-1]))
        plt.xlabel('Report Date')
        ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x,p: format(int(x),',')))
        ax.set_ylabel('Confirmed Cases')
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d/%y'))
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        ax.xaxis.set_minor_locator(mdates.DayLocator(bymonthday=(1,8,15,22)))
        plt.legend(loc='upper right')
        plt.savefig('/var/www/html/images/covid/metro_%s.png' % metroabbv[i],bbox_inches='tight')
        plt.close(fig)

        casetoday,caseweek,case2week,casemonth,casechange,case2change,case30change = \
                trends(metrodata['cases'].rolling(window=7).mean())
        case_trend.append(['%s' % i,'%0.0f' % casetoday,'%0.0f' % caseweek,'%0.0f' % case2week,\
            '%0.0f' % casemonth,'%0.3f' % casechange,'%0.3f' % case2change,'%0.3f' % case30change])

    makeCSV('/var/www/html/images/covid/metro_trends.csv',case_trend)

# create heatmap
print('Drawing heatmap')
hmdata = pd.read_csv('/var/www/html/images/covid/metro_trends.csv')
hmdata.set_index('metro area',inplace=True)
columns = ['7-day trend','14-day trend','30-day trend']
fig,ax = plt.subplots(figsize=(5,10))
ax = seaborn.heatmap(hmdata[columns]*100,annot=True,fmt='.1f',cbar_kws={'shrink':0.5,'orientation':\
    'vertical','format':'%.1f%%','extend':'both'},vmin=-50.0,vmax=50.0,cmap='RdBu_r',linewidths=1,\
    linecolor='white')
for t in ax.texts: t.set_text(t.get_text() + '%')
ax.tick_params(left=False,bottom=False)
ax.set_title('Metro Area Case Trends over the Past 7, 14, and 30 Days')
plt.savefig('/var/www/html/images/covid/metro_heatmap.png',bbox_inches='tight')
plt.close(fig)

print('Done.')
