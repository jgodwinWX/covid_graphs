import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mtick
import numpy
import pandas

# list of states

states = ['AL','AK','AZ','AR','CA','CO','CT','DC','DE','FL','GA','HI','ID','IL','IN','IA','KS','KY',\
    'LA','ME','MD','MA','MI','MN','MS','MO','MT','NE','NV','NH','NJ','NM','NY','NC','ND','OH',\
    'OK','OR','PA','RI','SC','SD','TN','TX','UT','VT','VA','WA','WV','WI','WY','PR','VI']
state_names = {'AL':'Alabama','AK':'Alaska','AZ':'Arizona','AR':'Arkansas','CA':'California'\
    ,'CO':'Colorado','CT':'Connecticut','DE':'Delaware','FL':'Florida','GA':'Georgia',\
    'HI':'Hawaii','ID':'Idaho','IL':'Illinois','IN':'Indiana','IA':'Iowa','KS':'Kansas'\
    ,'KY':'Kentucky','LA':'Louisiana','ME':'Maine','MD':'Maryland','MA':'Massachusetts',\
    'MI':'Michigan','MN':'Minnesota','MS':'Mississippi','MO':'Missouri','MT':'Montana',\
    'NE':'Nebraska','NV':'Nevada','NH':'New Hampshire','NJ':'New Jersey','NM':'New Mexico'\
    ,'NY':'New York','NC':'North Carolina','ND':'North Dakota','OH':'Ohio','OK':'Oklahoma'\
    ,'OR':'Oregon','PA':'Pennsylvania','RI':'Rhode Island','SC':'South Carolina',\
    'SD':'South Dakota','TN':'Tennessee','TX':'Texas','UT':'Utah','VT':'Vermont','VA':'Virginia'\
    ,'WA':'Washington','WV':'West Virginia','WI':'Wisconsin','WY':'Wyoming','PR':'Puerto Rico',\
    'VI':'U.S. Virgin Islands','DC':'District of Columbia'}

# FEMA regions
region1 = ['CT','ME','MA','NH','VT','RI']
region2 = ['NJ','NY']
region3 = ['DE','MD','PA','VA','WV']
region4 = ['AL','GA','FL','KY','MS','NC','SC','TN']
region5 = ['IL','IN','MI','MN','OH','WI']
region6 = ['AR','LA','NM','OK','TX']
region7 = ['IA','KS','MO','NE']
region8 = ['CO','MT','ND','SD','UT','WY']
region9 = ['AZ','CA','HI','NV']
region10 = ['AK','ID','OR','WA']
fema = [region1,region2,region3,region4,region5,region6,region7,region8,region9,region10]

# download the data
df = pandas.read_csv('https://covidtracking.com/api/v1/states/daily.csv',index_col='date')
state_data = {}

plt.close('all')
skip = False
for state in states:
    print(state)
    # parse the data out by state
    data = df[df['state']==state]
    # set the index as a datetime
    data.index = pandas.to_datetime(data.index,format='%Y%m%d')
    # create a week-over-week cases, deaths, and test column
    data['weeklyCases'] = data['positiveIncrease'][::-1].rolling(window=7).sum()[::-1]
    data['weeklyDeaths'] = data['deathIncrease'][::-1].rolling(window=7).sum()[::-1]
    data['weeklyTests'] = data['totalTestResultsIncrease'][::-1].rolling(window=7).sum()[::-1]
    # filter some values in Louisiana where the state stopped reporting commercial lab data
    if state == 'LA':
        blockdates = pandas.date_range(start='2020-04-19',end='2020-04-25')
        data.loc[data.index.isin(blockdates),'weeklyCases'] = numpy.nan
        data.loc[data.index.isin(blockdates),'weeklyTests'] = numpy.nan
    data['weeklyHospital'] = data['hospitalizedIncrease'][::-1].rolling(window=7).sum()[::-1]
    data['dailyPositivity'] = data['positiveIncrease']/data['totalTestResultsIncrease']
    data['weeklyPositivity'] = data['weeklyCases']/data['weeklyTests']

    data['dailyPositivity'] = numpy.where((data['dailyPositivity'] > 1.0),numpy.nan,data['dailyPositivity'])
    data['weeklyPositivity'] = numpy.where((data['weeklyPositivity'] > 1.0),numpy.nan,data['weeklyPositivity'])

    # we want to save this off for later use
    state_data[state] = data
    latest = data.index[0].strftime('%m/%d')
    if skip:
        continue
    # cumulative cases/deaths
    variables = [data['positive'],data['death']]
    names = ['Cases','Deaths']
    for y in range(len(variables)):
        fig,ax = plt.subplots()
        plt.plot(variables[y],marker='o',markevery=variables[y].size,color='blue')
        plt.text(variables[y].index[0],variables[y].values[0],'{0:,.0f}'.\
            format(variables[y].values[0]),color='blue')
        # aesthetics
        plt.grid(which='major',axis='x',linestyle='-',linewidth=2)
        plt.grid(which='minor',axis='x',linestyle='--')
        plt.grid(which='major',axis='y',linestyle='-')
        plt.title('Cumulative COVID-19 %s in %s\n(latest data: %s)' % (names[y],state_names[state],latest))
        plt.xlabel('Date')
        ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x,p: format(int(x),',')))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        ax.xaxis.set_minor_locator(mdates.DayLocator(bymonthday=(1,8,15,22)))
        if names[y] == 'Cases':
            plt.yscale('log')
            plt.ylabel('Cumulative Cases (log scale)')
            ax.yaxis.set_major_formatter(mtick.ScalarFormatter())
            ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x,p: format(int(x),',')))
            ### SAVE CUMULATIVE CASE FIGURE ###
            plt.savefig('/var/www/html/images/covid/positive_%s.png' % state,bbox_inches='tight')
        elif names[y] == 'Deaths':
            plt.ylabel('Cumulative Deaths')
            ### SAVE CUMULATIVE DEATH FIGURE ###
            plt.savefig('/var/www/html/images/covid/deaths_%s.png' % state,bbox_inches='tight')
        plt.clf()

    # week-over-week plots
    variables = [data['weeklyCases'],data['weeklyDeaths']]
    names = ['Cases','Deaths']
    for y in range(len(variables)):
        # first we want to plot week-over-week cases/tests and deaths
        fig,ax = plt.subplots()
        # plot cases/deaths
        ln1 = ax.plot(variables[y],label=names[y],marker='o',markevery=variables[y].size,color='blue')
        plt.text(variables[y].index[0],variables[y].values[0],'{0:,.0f}'.\
            format(variables[y].values[0]),color='blue')
        plt.grid(which='major',axis='x',linestyle='-',linewidth=2)
        plt.grid(which='minor',axis='x',linestyle='--')
        plt.grid(which='major',axis='y',linestyle='-')
        plt.title('Week-over-Week COVID-19 %s in %s\n(latest data: %s)' % (names[y],state_names[state],latest))
        plt.xlabel('Date')
        ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x,p: format(int(x),',')))
        # if we are on cases, we also want to plot tests
        if names[y] == 'Cases':
            # set up right axis
            ax2 = ax.twinx()
            ax2.set_ylabel('Week-over-Week Tests')
            ax2.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x,p: format(int(x),',')))
            # plot the tests
            ln2 = ax2.plot(data['weeklyTests'],label='Tests',marker='o',\
                markevery=data['weeklyTests'].size,color='red')
            plt.text(data['weeklyTests'].index[0],data['weeklyTests'].values[0],'{0:,.0f}'.\
                format(data['weeklyTests'].values[0]),color='red')
            ax.set_ylabel('Week-over-Week Cases')
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
            ax.xaxis.set_major_locator(mdates.MonthLocator())
            ax.xaxis.set_minor_locator(mdates.DayLocator(bymonthday=(1,8,15,22)))
            # logic for showing both lines in the legend
            leg = ln1 + ln2
            lab = [l.get_label() for l in leg]
            ax.legend(leg,lab,loc='upper left')
            ### SAVE WEEK-OVER-WEEK CASES/TESTS FIGURE ###
            plt.savefig('/var/www/html/images/covid/week_positive_%s.png' % state,\
                bbox_inches='tight')
        # plot week-over-week deaths
        elif names[y] == 'Deaths':
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
            ax.xaxis.set_major_locator(mdates.MonthLocator())
            ax.xaxis.set_minor_locator(mdates.DayLocator(bymonthday=(1,8,15,22)))
            plt.ylabel('Week-over-Week Deaths')
            # WEEK-OVER-WEEK DEATHS
            plt.savefig('/var/www/html/images/covid/week_deaths_%s.png' % state,\
                bbox_inches='tight')
        plt.clf()

    # plot week-over-week test positivity rate
    fig,ax = plt.subplots()
    plt.plot(data['weeklyPositivity'],marker='o',markevery=data['weeklyPositivity'].size,color='blue')
    plt.text(data['weeklyPositivity'].index[0],data['weeklyPositivity'].values[0],'{:,.1%}'.\
        format(data['weeklyPositivity'].values[0],color='blue'))
    plt.axhspan(0.0,0.1,color='#C8FFC8',alpha=0.5)
    plt.grid(which='major',axis='x',linestyle='-',linewidth=2)
    plt.grid(which='minor',axis='x',linestyle='--')
    plt.grid(which='major',axis='y',linestyle='-')
    plt.title('Week-over-Week Test Positivity Rate in %s\n(latest data: %s)' % (state_names[state],latest))
    plt.xlabel('Date')
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_minor_locator(mdates.DayLocator(bymonthday=(1,8,15,22)))
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
    plt.ylabel('Test Positivity Rate')
    # SAVE WEEK-OVER-WEEK TEST POSITIVITY FIGURE ###
    plt.savefig('/var/www/html/images/covid/week_testpos_%s.png' % state,bbox_inches='tight')
    plt.clf()

    # currently hospitalized
    fig,ax = plt.subplots()
    rects = ax.bar(x=data.index,height=data['hospitalizedCurrently'],color='blue')
    plt.grid(which='major',axis='y',linestyle='-')
    plt.grid(which='both',axis='x',linestyle='--')
    plt.title('Daily COVID-19 Hospitalizations in %s\n(latest data: %s)' % (state_names[state],latest))
    plt.xlabel('Date')
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_minor_locator(mdates.DayLocator(bymonthday=(1,8,15,22)))
    ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x,p: format(int(x),',')))
    for rect in rects:
        height = rect.get_height()
        ax.annotate('{0:,.0f}'.format(height),xy=(rect.get_x()+rect.get_width()/2,height),\
            xytext=(0,3),textcoords='offset points',ha='center',va='bottom',rotation=90,size=8)
    plt.ylabel('Hospitalizations')
    ### SAVE DAILY HOSPITALIZATION FIGURE ###
    plt.savefig('/var/www/html/images/covid/hospitalized_%s.png' % state,bbox_inches='tight')
    plt.clf()

    # test-positivity
    fig,ax = plt.subplots()
    plt.plot(data['dailyPositivity'],marker='o',markevery=data['dailyPositivity'].size,color='blue')
    plt.text(data['dailyPositivity'].index[0],data['dailyPositivity'].values[0],'{:,.1%}'.\
        format(data['dailyPositivity'].values[0],color='blue'))
    plt.axhspan(0.0,0.1,color='#C8FFC8',alpha=0.5)
    # aesthetics
    plt.grid(which='major',axis='x',linestyle='-',linewidth=2)
    plt.grid(which='minor',axis='x',linestyle='--')
    plt.grid(which='major',axis='y',linestyle='-')
    plt.title('Daily Test Positivity Rate in %s\n(latest data: %s)' % (state_names[state],latest))
    plt.xlabel('Date')
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_minor_locator(mdates.DayLocator(bymonthday=(1,8,15,22)))
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
    plt.ylabel('Test Positivity Rate')
    ### SAVE DAILY TEST-POSITIVITY FIGURE ###
    plt.savefig('/var/www/html/images/covid/testpos_%s.png' % state,bbox_inches='tight')
    plt.clf()

    plt.close('all')

# FEMA regions

for ix,region in enumerate(fema):
    print('FEMA Region %s' % str(ix+1))
    # cumulative cases/deaths
    variables = ['positive','death']
    names = ['Cases','Deaths']
    for y in range(len(variables)):
        fig,ax = plt.subplots()
        for state in region:
            ln = ax.plot(state_data[state][variables[y]],label=state,marker='o',\
                markevery=state_data[state][variables[y]].size)
            plt.text(state_data[state][variables[y]].index[0],state_data[state][variables[y]].\
                values[0],'{0:,.0f}'.format(state_data[state][variables[y]].values[0]),\
                color=ln[0].get_color(),size=8)
        # aesthetics
        region_data = pandas.concat([state_data[x] for x in region],axis=0)
        region_data_plot = region_data.groupby(region_data.index)[variables[y]].sum().\
            reset_index(name=variables[y]).set_index('date')
        plt.plot(region_data_plot,label='Region Total',color='k',linewidth=2,marker='o',\
            markevery=region_data_plot.size)
        plt.text(region_data_plot.index[-1],region_data_plot.values[-1],'{0:,.0f}'.\
            format(float(region_data_plot.values[-1])),color='k')
        plt.grid(which='major',axis='x',linestyle='-',linewidth=2)
        plt.grid(which='minor',axis='x',linestyle='--')
        plt.grid(which='major',axis='y',linestyle='-')
        plt.title('Cumulative COVID-19 %s in FEMA Region %d' % (names[y],ix+1))
        plt.xlabel('Date')
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        ax.xaxis.set_minor_locator(mdates.DayLocator(bymonthday=(1,8,15,22)))
        ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x,p: format(int(x),',')))
        ax.legend(loc='upper left')
        if names[y] == 'Cases':
            plt.yscale('log')
            plt.ylabel('Cumulative Cases (log scale)')
            ax.yaxis.set_major_formatter(mtick.ScalarFormatter())
            ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x,p: format(int(x),',')))
            ### SAVE FEMA REGION CASES FIGURE ###
            plt.savefig('/var/www/html/images/covid/positive_fema_%s.png' % str(ix+1).zfill(2),\
                bbox_inches='tight')
        elif names[y] == 'Deaths':
            plt.ylabel('Cumulative Deaths')
            ### SAVE FEMA REGION DEATHS FIGURE ###
            plt.savefig('/var/www/html/images/covid/deaths_fema_%s.png' % str(ix+1).zfill(2),\
                bbox_inches='tight')
        plt.clf()

    # hospitalized
    fig,ax = plt.subplots()
    region_data_hos = region_data.groupby(region_data.index)['hospitalizedCurrently'].sum().\
        reset_index(name='hospitalizedCurrently').set_index('date')
    fema_rects = ax.bar(x=region_data_hos.index,height=region_data_hos['hospitalizedCurrently'])
    plt.grid(which='major',axis='y',linestyle='-')
    plt.grid(which='both',axis='x',linestyle='--')
    plt.title('COVID-19 Hospitalizations in FEMA Region %s' % str(ix+1).zfill(2))
    plt.xlabel('Date')
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_minor_locator(mdates.DayLocator(bymonthday=(1,8,15,22)))
    ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x,p: format(int(x),',')))
    for rect in fema_rects:
        height = rect.get_height()
        ax.annotate('{0:,.0f}'.format(height),xy=(rect.get_x()+rect.get_width()/2,height),\
            xytext=(0,3),textcoords='offset points',ha='center',va='bottom',rotation=90,size=8)
    plt.ylabel('Hospitalizations')
    ### SAVE FEMA REGION HOSPITALIZATIONS FIGURE ###
    plt.savefig('/var/www/html/images/covid/hospitalized_fema_%s.png' % str(ix+1).zfill(2),\
        bbox_inches='tight')
    plt.clf()

    plt.close('all')

# compute some stuff
dailytopfive = df.set_index("state", append=True).groupby(level=0)["positiveIncrease"].nlargest(5)
