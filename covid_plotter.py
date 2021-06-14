# -*- coding: utf-8 -*-
"""
Created on Mon Mar 29 15:27:30 2021

@author: Jason W. Godwin

"""

import csv
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mtick
import numpy as np
import pandas as pd
import seaborn

from functools import reduce
from sodapy import Socrata

# function for getting current, 7 days ago, 14 days ago, 30 days, and trends
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

# testing options
testmode = False        # limit results to one state in order to test?
teststate = 'TX'        # state to test on if running a single state
runcumulative = True    # run the cumulative cases/deaths plots?
runcasedeath = True     # run the daily cases/deaths plots?
runexcess = True        # run the excess mortality plots?
runhospital = True      # run the hospitalizations plots?
runtesting = True       # run the total test plots?
runpositivity = True    # run the positivity plots?

# directory to which to save output
savedir = '/var/www/html/images/covid'
# how many days back to look at the data
window = 180

# case and death data from the CDC
print('Accessing data APIs')
client = Socrata('data.cdc.gov',None)
results = client.get('9mfq-cb36',limit=50000)
cases_df = pd.DataFrame.from_records(results)
cases_df.sort_values('submission_date',inplace=True)
cases_df['submission_date'] = pd.to_datetime(cases_df['submission_date'],\
                                             format='%Y-%m-%dT%H:%M:%S.000')
cases_df.set_index('submission_date',inplace=True)
fields = ['tot_cases','new_case','tot_death','new_death']
for field in fields:
    cases_df[field] = pd.to_numeric(cases_df[field],errors='coerce',downcast='float')    
cases_df['new_case'].mask(cases_df['new_case'] < 0,inplace=True)
cases_df['new_death'].mask(cases_df['new_death'] < 0,inplace=True)

# excess mortality data from the CDC
em_results = client.get('xkkf-xrst',limit=50000)
em = pd.DataFrame.from_records(em_results)
fields= ['excess_lower_estimate','excess_higher_estimate']
for field in fields:
    em[field] = pd.to_numeric(em[field],errors='coerce',downcast='float')
em['week_ending_date'] = pd.to_datetime(em['week_ending_date'],format='%Y-%m-%d')
em.set_index('week_ending_date',inplace=True)

# hospitalization data from HHS
# This is broken and due to poor documentation from API maintainers, I am unsure as to how
# to request the right range of data. Any feedback/help is appreciated.
hhs_client = Socrata('healthdata.gov',None)
hhs_results = hhs_client.get('g62h-syeh',order='date',offset=15000,limit=10000)
hhs_df = pd.DataFrame.from_records(hhs_results)
hhs_df.sort_values('date',inplace=True)
hhs_df['date'] = pd.to_datetime(hhs_df['date'],format='%Y-%m-%dT%H:%M:%S.000')
hhs_df.set_index('date',inplace=True)
fields = ['inpatient_beds_used_covid','inpatient_bed_covid_utilization']
for field in fields:
    hhs_df[field] = pd.to_numeric(hhs_df[field],errors='coerce',downcast='float')
hhs_df['inpatient_bed_covid_utilization'] = hhs_df['inpatient_bed_covid_utilization'] * 100.0

# testing data from HHS
testing_results = hhs_client.get('j8mb-icvb',limit=80000)
testing_df = pd.DataFrame.from_records(testing_results)
testing_df.sort_values('date',inplace=True)
testing_df['date'] = pd.to_datetime(testing_df['date'],format='%Y-%m-%dT%H:%M:%S.000')
testing_df.set_index('date',inplace=True)
testing_df['new_results_reported'] = pd.to_numeric(testing_df['new_results_reported'],\
    errors='coerce',downcast='float')

# case and death plots
states = set(cases_df['state'])
state_names = {'AK':'Alaska','AL':'Alabama','AR':'Arkansas','AS':'American Samoa','AZ':'Arizona',\
               'CA':'California','CO':'Colorado','CT':'Connecticut','DC':'District of Columbia',\
               'DE':'Delaware','FL':'Florida','FSM':'Federated States of Micronesia',\
               'GA':'Georgia','GU':'Guam','HI':'Hawaii','IA':'Iowa','ID':'Idaho','IL':'Illinois',\
               'IN':'Indiana','KS':'Kansas','KY':'Kentucky','LA':'Louisiana','MA':'Massachusetts',\
               'MD':'Maryland','ME':'Maine','MI':'Michigan','MN':'Minnesota','MO':'Missouri',\
               'MP':'Northern Mariana Islands','MS':'Mississippi','MT':'Montana',\
               'NC':'North Carolina','ND':'North Dakota','NE':'Nebraska','NH':'New Hampshire',\
               'NJ':'New Jersey','NM':'New Mexico','NV':'Nevada','NY':'New York (outside NYC)',\
               'NYC':'New York City','OH':'Ohio','OK':'Oklahoma','OR':'Oregon',\
               'PA':'Pennsylvania','PR':'Puerto Rico','PW':'Palau','RI':'Rhode Island',\
               'RMI':'Marshall Islands','SC':'South Carolina','SD':'South Dakota',\
               'TN':'Tennessee','TX':'Texas','UT':'Utah','VA':'Virginia',\
               'VI':'U.S. Virgin Islands','VT':'Vermont','WA':'Washington','WI':'Wisconsin',\
               'WV':'West Virginia','WY':'Wyoming'}
abbreviations = {'Alabama':'AL','Alaska':'AK','Arizona':'AZ','Arkansas':'AR','California':'CA',\
               'Colorado':'CO','Connecticut':'CT','Delaware':'DE','District of Columbia':'DC',\
               'Florida':'FL','Georgia':'GA','Hawaii':'HI','Idaho':'ID','Illinois':'IL',\
               'Indiana':'IN','Iowa':'IA','Kansas':'KS','Kentucky':'KY','Louisiana':'LA',\
               'Maine':'ME','Maryland':'MD','Massachusetts':'MA','Michigan':'MI','Minnesota':'MN',\
               'Mississippi':'MS','Missouri':'MO','Montana':'MT','Nebraska':'NE','Nevada':'NV',\
               'New Hampshire':'NH','New Jersey':'NJ','New Mexico':'NM','New York City':'NYC',\
               'New York':'NY','North Carolina':'NC','North Dakota':'ND','Ohio':'OH',\
               'Oklahoma':'OK','Oregon':'OR','Pennsylvania':'PA','Puerto Rico':'PR',\
               'Rhode Island':'RI','South Carolina':'SC','South Dakota':'SD','Tennessee':'TN',\
               'Texas':'TX','United States':'US','Utah':'UT','Vermont':'VT','Virginia':'VA',\
               'Washington':'WA','West Virginia':'WV','Wisconsin':'WI','Wyoming':'WY'}

# skip the states/jurisdictions with incomplete data
skipstates = ['RMI','AS','FSM','PW','MH']

# cumulative cases
for state in states:
    if not runcumulative:
        break
    if testmode and state != teststate or state in skipstates:
        continue
    print('%s: Cumulative' % state)
    state_df = cases_df[cases_df['state']==state]
    fig,ax = plt.subplots(figsize=(12,8))
    plt.plot(state_df['tot_cases'],label='Total Cases',color='blue',marker='o',\
             markevery=state_df['tot_cases'].size-1)
    plt.text(state_df['tot_cases'].index[-1],state_df['tot_cases'][-1],'{0:,.0f}'.\
             format(state_df['tot_cases'][-1]),color='blue')
    plt.plot(state_df['tot_death'],label='Total Deaths',color='red',marker='o',\
             markevery=state_df['tot_death'].size-1)
    plt.text(state_df['tot_death'].index[-1],state_df['tot_death'][-1],'{0:,.0f}'.\
             format(state_df['tot_death'][-1]),color='red')
    plt.grid(which='major',axis='x',linestyle='-',linewidth=2)
    plt.grid(which='minor',axis='x',linestyle='--')
    plt.grid(which='major',axis='y',linestyle='-')
    plt.title('Cumulative COVID-19 Cases and Deaths in %s' % state_names[state])
    plt.xlabel('Date')
    plt.xticks(rotation=30,ha='right')
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d/%y'))
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_minor_locator(mdates.DayLocator(bymonthday=(1,8,15,22)))
    plt.yscale('log')
    plt.ylabel('Cases/Deaths (logarthmic)')
    ax.yaxis.set_major_formatter(mtick.ScalarFormatter())
    ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x,p: format(int(x),',')))
    plt.legend(loc='lower right')
    plt.savefig('%s/log_cases_%s.png' % (savedir,state.lower()),bbox_inches='tight')
    plt.close(fig)

# daily cases and deaths
if runcasedeath:
    data = ['new_case','new_death']
    datasets = {'new_case':'Daily New Cases','new_death':'Daily New Deaths'}
    basicdata = {'new_case':'Cases','new_death':'Deaths'}
    case_trend = [['state','new cases','one week ago (cases)','two weeks ago (cases)',\
        '30 days ago (cases)','7-day trend (cases)','14-day trend (cases)','30-day trend (cases)']]
    death_trend = [['state','new deaths','one week ago (deaths)','two weeks ago (deaths)',\
        '30 days ago (deaths)','7-day trend (deaths)','14-day trend (deaths)',\
        '30-day trend (deaths)']]

    # loop through each state and each dataset
    for state in states:
        for i in data:
            if testmode and state != teststate or state in skipstates:
                continue
            print('%s: %s' % (state_names[state],datasets[i]))
            state_df = cases_df[cases_df['state']==state]
            # filter outlier values to account for backlogged reporting
            if state_df[i].nlargest(5)[0] / state_df[i].nlargest(5)[4] >= 1.5:
                state_df[i].mask(state_df[i] >= state_df[i].nlargest(5)[4] * 1.5,inplace=True)
            # create the plots for daily cases/deaths and 7-day moving averages
            fig,ax = plt.subplots(figsize=(12,8))
            plt.bar(state_df.index[-window:],state_df[i][-window:],color='blue',label=datasets[i])
            plt.plot(state_df[i].rolling(window=7).mean()[-window:],color='red',\
                label='7-Day Moving Average',marker='o',markevery=[-1])
            # plot a point at the most recent value
            plt.text(state_df.index[-1],state_df[i].rolling(window=7).mean()[-1],'{0:,.0f}'.\
                format(state_df[i].rolling(window=7).mean()[-1]),color='red')
            # plot aesthetics
            plt.grid(which='major',axis='x',linestyle='-',linewidth=2)
            plt.grid(which='minor',axis='x',linestyle='--')
            plt.grid(which='major',axis='y',linestyle='-')
            latest = state_df.index[-1].strftime('%d %b %y')
            plt.title('Last %i Days of %s in %s\n(latest data: %s)' \
                % (window,datasets[i],state_names[state],latest))
            plt.xlabel('Report Date')
            plt.ylabel(basicdata[i])
            ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x,p: format(int(x),',')))
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d/%y'))
            ax.xaxis.set_major_locator(mdates.MonthLocator())
            ax.xaxis.set_minor_locator(mdates.DayLocator(bymonthday=(1,8,15,22)))
            plt.xticks(rotation=30,ha='right')
            plt.legend(loc='upper right')
            plt.savefig('%s/%s_%s.png' % (savedir,basicdata[i].lower(),state.lower()),\
                bbox_inches='tight')
            plt.close(fig)
            # save off case and death trend data
            casetoday,caseweek,case2week,casemonth,casechange,case2change,case30change = \
                trends(state_df[i].rolling(window=7).mean())
            if i == 'new_case':
                case_trend.append(['%s' % state,'%0.0f' % casetoday,'%0.0f' % caseweek,\
                    '%0.0f' % case2week,'%0.0f' % casemonth,'%0.1f%%' % (casechange*100),\
                    '%0.1f%%' % (case2change*100),'%0.1f%%' % (case30change*100)])
            if i == 'new_death':
                death_trend.append(['%s' % state,'%0.0f' % casetoday,'%0.0f' % caseweek,\
                    '%0.0f' % case2week,'%0.0f' % casemonth,'%0.1f%%' % (casechange*100),\
                    '%0.1f%%' % (case2change*100),'%0.1f%%' % (case30change*100)])
    # write out case and death trend data
    files = ['%s/case_trends.csv' % savedir,'%s/death_trends.csv' % savedir]
    info = [case_trend,death_trend]
    for i,j in enumerate(files):
        makeCSV(j,info[i])
        
# excess mortality plots
if runexcess:
    states = set(em['state'])
    # loop through each state
    for state in states:
        if testmode and state != 'Texas':
            continue
        print("%s: excess mortality" % state)
        # get the state-level data
        state_em = em[em['state']==state]
        # plot the weekly numbers on the left axis, and cumulative numbers on the right axis
        fig,ax1 = plt.subplots(figsize=(12,8))
        ax2 = ax1.twinx()
        ax1.plot(state_em['excess_lower_estimate'][-52:],color='blue',\
            label='Weekly Excess Mortality (lower estimate)')
        ax1.plot(state_em['excess_higher_estimate'][-52:],color='red',\
            label='Weekly Excess Mortality (upper estimate)')
        ax2.plot(state_em['excess_lower_estimate'][-52:].cumsum(),color='black',\
            label='Cumulative Excess Mortality',marker='o',markevery=[-1])
        # plot a point at the cumulative total
        plt.text(state_em.index[-1],state_em['excess_lower_estimate'][-52:].cumsum()[-1],'{0:,.0f}'.\
            format(state_em['excess_lower_estimate'][-52:].cumsum()[-1]),color='black')
        # plot aesthetics
        ax1.grid(which='major',axis='x',linestyle='-',linewidth=2)
        ax1.grid(which='minor',axis='x',linestyle='--')
        ax1.grid(which='major',axis='y',linestyle='-')
        plt.title('Last 52 Weeks Excess Mortality in %s\n(last few weeks may not be reported yet!)' \
            % state)
        ax1.set_xlabel('Month')
        ax1.set_ylabel('Weekly Excess Deaths')
        ax2.set_ylabel('Total Excess Deaths')
        ax1.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x,p: format(int(x),',')))
        ax2.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x,p: format(int(x),',')))
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%b %y'))
        ax1.xaxis.set_major_locator(mdates.MonthLocator())
        ax1.xaxis.set_minor_locator(mdates.DayLocator(bymonthday=(1,8,15,22)))
        ax1.legend(loc='upper left')
        plt.savefig('%s/excess_%s.png' % (savedir,abbreviations[state].lower()),bbox_inches='tight')
        plt.close(fig)
    
# hospitalization data
if runhospital:
    states = set(hhs_df['state'])
    datasets = {'inpatient_beds_used_covid':'Inpatients currently hospitalized with COVID-19',
                'inpatient_bed_covid_utilization':\
                    'Percentage of total inpatient beds with COVID-19 inpatients'}
    basicdata = {'inpatient_beds_used_covid':'Beds','inpatient_bed_covid_utilization':'Percent'}
    hosp_trend = [['state','hospitalized','one week ago (hosp)','two weeks ago (hosp)',\
        '30 days ago (hosp)','7-day trend (hosp)','14-day trend (hosp)','30-day trend (hosp)']]

    # loop through each state and each dataset
    for state in states:
        for dataset in datasets:
            if testmode and state != 'TX':
                continue
            if state in skipstates:
                continue
            print('%s: %s' % (state_names[state],dataset))
            # get the state-level data
            state_hhs = hhs_df[hhs_df['state']==state]
            # plot the hospitalization daily data
            fig,ax = plt.subplots(figsize=(12,8))
            plt.bar(state_hhs.index[-window:],state_hhs[dataset][-window:],color='blue',\
                label=datasets[dataset])
            # plot the seven-day moving average
            plt.plot(state_hhs[dataset][-window:].rolling(window=7).mean(),color='red',\
                label='7-Day Moving Average',marker='o',markevery=[-1])
            # plot aesthetics
            plt.grid(which='major',axis='x',linestyle='-',linewidth=2)
            plt.grid(which='minor',axis='x',linestyle='--')
            plt.grid(which='major',axis='y',linestyle='-')
            latest = state_hhs.index[-1].strftime('%d %b %y')
            plt.title('Last %i Days of %s in %s\n(latest data: %s)' \
                      % (window,datasets[dataset],state_names[state],latest))
            plt.xlabel('Report Date')
            plt.ylabel(basicdata[dataset])
            # format the axes and plot the most recent data depending on which dataset
            if dataset == 'inpatient_beds_used_covid':
                ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x,p: format(int(x),',')))
                plt.text(state_hhs.index[-1],state_hhs[dataset][-1]+state_hhs[dataset][-1]*0.1,\
                    '{0:,.0f}'.format(state_hhs[dataset].rolling(window=7).mean()[-1]),color='red')
            elif dataset == 'inpatient_bed_covid_utilization':
                plt.text(state_hhs.index[-1],state_hhs[dataset][-1]+2,'{0:,.1f}%'.\
                    format(state_hhs[dataset][-1]),color='red')
                ax.yaxis.set_major_formatter(mtick.PercentFormatter())
                plt.ylim([0,100])
                plt.yticks(np.arange(0,101,5))
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d/%y'))
            ax.xaxis.set_major_locator(mdates.MonthLocator())
            ax.xaxis.set_minor_locator(mdates.DayLocator(bymonthday=(1,8,15,22)))
            plt.xticks(rotation=30,ha='right')
            plt.legend(loc='upper right')
            plt.savefig('%s/%s_%s.png' % (savedir,basicdata[dataset].lower(),state.lower()),\
                bbox_inches='tight')
            plt.close(fig)
            # save off hospitalization data
            if dataset == 'inpatient_beds_used_covid':
                hosptoday,hospweek,hosp2week,hospmonth,hospchange,hosp2change,hosp30change = \
                    trends(state_hhs[dataset].rolling(window=7).mean())
                hosp_trend.append(['%s' % state,'%0.0f' % hosptoday,'%0.0f' % hospweek,\
                        '%0.0f' % hosp2week,'%0.0f' % hospmonth,'%0.1f%%' % (hospchange*100),\
                        '%0.1f%%' % (hosp2change*100),'%0.1f%%' % (hosp30change*100)])
    # write out case and death trend data
    makeCSV('%s/hosp_trends.csv' % savedir,hosp_trend)

# total testing
if runtesting:
    # loop through each state
    for state in set(testing_df['state']):
        if testmode and state != 'TX' or state in skipstates:
            continue
        print('%s: testing' % state)
        # get the state-level testing data
        tests = testing_df[(testing_df['state']==state)]['new_results_reported'].groupby(['date'])\
            .sum()
        # plot the daily number of tests and the 7-day moving average
        fig,ax = plt.subplots(figsize=(12,8))
        plt.bar(tests.index[-window:],tests[-window:],color='blue',label='Total Tests Conducted')
        plt.plot(tests[-window:].rolling(window=7).mean(),color='red',label='7-Day Moving Average',\
            marker='o',markevery=[-1])
        # plot aesthetics
        plt.grid(which='major',axis='x',linestyle='-',linewidth=2)
        plt.grid(which='minor',axis='x',linestyle='--')
        plt.grid(which='major',axis='y',linestyle='-')
        latest = tests.index[-1].strftime('%d %b %y')
        plt.title('Last %i Days of Tests Conducted in %s\n(latest data: %s)' \
                  % (window,state_names[state],latest))
        plt.xlabel('Report Date')
        plt.ylabel('Tests Conducted')
        # plot a point at the most recent data point
        plt.text(tests.index[-1],tests.rolling(window=7).mean()[-1],'{0:,.0f}'\
            .format(tests.rolling(window=7).mean()[-1]),color='red')
        ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x,p: format(int(x),',')))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d/%y'))
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        ax.xaxis.set_minor_locator(mdates.DayLocator(bymonthday=(1,8,15,22)))
        plt.xticks(rotation=30,ha='right')
        plt.legend(loc='upper right')
        plt.savefig('%s/testing_%s.png' % (savedir,state.lower()),bbox_inches='tight')
        plt.close(fig)

# positivity rate
if runpositivity:
    pos_trend = [['state','positivity','one week ago (%)','two weeks ago (%)','30 days ago (%)',\
        '7-day trend (%)','14-day trend (%)','30-day trend (%)']]
    for state in set(testing_df['state']):
        if testmode and state != 'TX' or state in skipstates:
            continue
        print('%s: positivity' % state)
        # compute daily positivity
        ''' EXPLANATION OF DAILY POSITIVITY
        The HHS database has an individual line for state,date,outcome. This means that each date
        has up to three lines: positive results, negative results, and inconclusive results. For 
        this reason, we look for where the row matches a certain state and outcome=positive to get
        the positive results, and then divide it by the rows that match a certain state and are
        grouped by date to get the total number of reported tests.
        '''
        positivity = (testing_df[(testing_df['state']==state) & \
            (testing_df['overall_outcome']=='Positive')]['new_results_reported']) / \
            (testing_df[(testing_df['state']==state)]['new_results_reported'].groupby(['date'])\
            .sum())
        # compute the 7-day moving positivity
        ''' EXPLANATION OF THE 7-DAY AVERAGE POSITIVITY 
        The 7-day moving is similar, except we apply .rolling(window=7).sum() to get the seven-
        day total positive divided by the seven-day total cases. This will NOT produce the same
        value as dividing the seven-day average cases (which uses .rolling(window=7).mean() by 
        the seven-day average testing because for this value, we are getting the grand total seven-
        day positivity, not the average seven-day positivity for each day. This allows us to smooth
        out differences in reported tests each day.
        '''
        positivity_week = (testing_df[(testing_df['state']==state) & \
            (testing_df['overall_outcome']=='Positive')]['new_results_reported'].rolling(window=7)\
            .sum()) / (testing_df[(testing_df['state']==state)]\
            ['new_results_reported'].groupby(['date']).sum().rolling(window=7).sum())
        # plot the daily positivity and the 7-day moving positivity
        fig,ax = plt.subplots(figsize=(12,8))
        plt.bar(positivity.index[-window:],positivity[-window:]*100,color='blue',\
            label='Positivity Rate')
        plt.plot(positivity_week[-window:]*100,color='red',label='7-Day Moving Average',marker='o',\
            markevery=[-1])
        # plot aesthetics
        plt.grid(which='major',axis='x',linestyle='-',linewidth=2)
        plt.grid(which='minor',axis='x',linestyle='--')
        plt.grid(which='major',axis='y',linestyle='-')
        latest = positivity.index[-1].strftime('%d %b %y')
        plt.title('Last %i Days of Positivity Rate in %s\n(latest data: %s)' \
                  % (window,state_names[state],latest))
        plt.xlabel('Report Date')
        plt.ylabel('Positivity Rate')
        plt.text(positivity_week.index[-1],positivity_week[-1]*100+2,'{0:,.1f}%'.\
                format(positivity_week[-1]*100.0),color='red')
        ax.yaxis.set_major_formatter(mtick.PercentFormatter())
        plt.ylim([0,50])
        plt.yticks(np.arange(0,51,2))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d/%y'))
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        ax.xaxis.set_minor_locator(mdates.DayLocator(bymonthday=(1,8,15,22)))
        plt.xticks(rotation=30,ha='right')
        plt.legend(loc='upper right')
        plt.savefig('%s/positivity_%s.png' % (savedir,state.lower()),bbox_inches='tight')
        plt.close(fig)
        # save off positivity data
        postoday,posweek,pos2week,posmonth,poschange,pos2change,pos30change = \
            trends(positivity_week,True)
        pos_trend.append(['%s' % state,'%0.1f%%' % (postoday*100),'%0.1f%%' % (posweek*100),\
            '%0.1f%%' % (pos2week*100),'%0.1f%%' % (posmonth*100),'%0.1f' % (poschange*100),\
            '%0.1f' % (pos2change*100),'%0.1f' % (pos30change*100)])
    # write out case and death trend data
    makeCSV('%s/pos_trends.csv' % savedir,pos_trend)

# create master CSV
print('Creating master trend CSV')
csvs = ['case_trends.csv','death_trends.csv','hosp_trends.csv','pos_trends.csv']
dfs = [None]*len(csvs)
for x,y in enumerate(csvs):
    dfs[x] = pd.read_csv('%s/%s' % (savedir,y))

df_merged = reduce(lambda left,right: pd.merge(left,right,on=['state'],how='outer'),dfs)
df_merged.set_index('state',inplace=True)
df_merged.to_csv('%s/master_trends.csv' % savedir)

# create heatmap
print('Drawing heatmap')
hmdata = pd.read_csv('%s/master_trends.csv' % savedir)
# remove the percent signs
columns = ['7-day trend (cases)','7-day trend (deaths)','7-day trend (hosp)',\
    '14-day trend (cases)','14-day trend (deaths)','14-day trend (hosp)','30-day trend (cases)',\
    '30-day trend (deaths)','30-day trend (hosp)']
for i in columns: hmdata[i] = hmdata[i].str.replace('%','').astype(float)
hmdata.set_index('state',inplace=True)
hmdata.sort_index(inplace=True)
fig,ax = plt.subplots(figsize=(10,20))
ax = seaborn.heatmap(hmdata[columns],annot=True,fmt='.1f',cbar_kws={'shrink':0.5,'orientation':\
    'vertical','format':'%.1f%%','extend':'both'},vmin=-50.0,vmax=50.0,cmap='RdBu_r',linewidths=1,\
    linecolor='white')
for t in ax.texts: t.set_text(t.get_text() + '%')
ax.tick_params(left=False,bottom=False)
ax.set_title('State Trends over the Past 7, 14, and 30 Days')
plt.savefig('%s/heatmap.png' % savedir,bbox_inches='tight')
plt.close(fig)

print('Done')
