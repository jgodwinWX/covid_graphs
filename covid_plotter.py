# -*- coding: utf-8 -*-
"""
Created on Mon Mar 29 15:27:30 2021

@author: Jason W. Godwin
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mtick
import numpy as np
import pandas as pd

from sodapy import Socrata

testmode = False
savedir = '/var/www/html/images/covid'
# how many days back to look at the data
window = 180

# case and death data from the CDC
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
hhs_client = Socrata('healthdata.gov',None)
hhs_results = hhs_client.get('g62h-syeh',limit=50000)
hhs_df = pd.DataFrame.from_records(hhs_results)
hhs_df.sort_values('date',inplace=True)
hhs_df['date'] = pd.to_datetime(hhs_df['date'],format='%Y-%m-%dT%H:%M:%S.000')
hhs_df.set_index('date',inplace=True)
fields = ['inpatient_beds_used_covid','inpatient_bed_covid_utilization']
for field in fields:
    hhs_df[field] = pd.to_numeric(hhs_df[field],errors='coerce',downcast='float')
hhs_df['inpatient_bed_covid_utilization'] = hhs_df['inpatient_bed_covid_utilization'] * 100.0

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
               'NJ':'New Jersey','NM':'New Mexico','NV':'Nevada','NY':'New York',\
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
               'New Hampshire':'NH','New Jersey':'NJ','New Mexico':'NM','New York City':'NY',\
               'New York':'NY','North Carolina':'NC','North Dakota':'ND','Ohio':'OH',\
               'Oklahoma':'OK','Oregon':'OR','Pennsylvania':'PA','Puerto Rico':'PR',\
               'Rhode Island':'RI','South Carolina':'SC','South Dakota':'SD','Tennessee':'TN',\
               'Texas':'TX','United States':'US','Utah':'UT','Vermont':'VT','Virginia':'VA',\
               'Washington':'WA','West Virginia':'WV','Wisconsin':'WI','Wyoming':'WY'}

# skip the states/jurisdictions with incomplete data
skipstates = ['RMI','AS','FSM','PW']

# cumulative cases
for state in states:
    if testmode and state != 'TX':
        continue
    if state in skipstates:
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
data = ['new_case','new_death']
datasets = {'new_case':'Daily New Cases','new_death':'Daily New Deaths'}
basicdata = {'new_case':'Cases','new_death':'Deaths'}

for state in states:
    for i in data:
        if testmode and state != 'TX':
            continue
        if state in skipstates:
            continue
        print('%s: %s' % (state_names[state],datasets[i]))
        state_df = cases_df[cases_df['state']==state]
        # filter outlier values
        if state_df[i].nlargest(5)[0] / state_df[i].nlargest(5)[4] >= 1.5:
            state_df[i].mask(state_df[i] >= state_df[i].nlargest(5)[4] * 1.5,inplace=True)
        # create the plots for daily cases
        fig,ax = plt.subplots(figsize=(12,8))
        plt.bar(state_df.index[-window:],state_df[i][-window:],color='blue',label=datasets[i])
        plt.plot(state_df[i].rolling(window=7).mean()[-window:],color='red',\
            label='7-Day Moving Average',marker='o',markevery=[-1])
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
        
# excess mortality plots
states = set(em['state'])
for state in states:
    if testmode and state != 'Texas':
        continue
    print("%s: excess mortality" % state)
    state_em = em[em['state']==state]
    fig,ax1 = plt.subplots(figsize=(12,8))
    ax2 = ax1.twinx()
    ax1.plot(state_em['excess_lower_estimate'][-52:],color='blue',\
        label='Weekly Excess Mortality (lower estimate)')
    ax1.plot(state_em['excess_higher_estimate'][-52:],color='red',\
        label='Weekly Excess Mortality (upper estimate)')
    ax2.plot(state_em['excess_lower_estimate'][-52:].cumsum(),color='black',\
        label='Cumulative Excess Mortality',marker='o',markevery=[-1])
    plt.text(state_em.index[-1],state_em['excess_lower_estimate'][-52:].cumsum()[-1],'{0:,.0f}'.\
        format(state_em['excess_lower_estimate'][-52:].cumsum()[-1]),color='black')
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
states = set(hhs_df['state'])
datasets = {'inpatient_beds_used_covid':'Inpatients currently hospitalized with COVID-19',
            'inpatient_bed_covid_utilization':\
                'Percentage of total inpatient beds with COVID-19 inpatients'}
basicdata = {'inpatient_beds_used_covid':'Beds','inpatient_bed_covid_utilization':'Percent'}
    
for state in states:
    for dataset in datasets:
        if testmode and state != 'TX':
            continue
        if state in skipstates:
            continue
        print('%s: %s' % (state_names[state],dataset))
        state_hhs = hhs_df[hhs_df['state']==state]
        fig,ax = plt.subplots(figsize=(12,8))
        plt.bar(state_hhs.index[-window:],state_hhs[dataset][-window:],color='blue',\
            label=datasets[dataset])
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
        if dataset == 'inpatient_beds_used_covid':
            ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x,p: format(int(x),',')))
            plt.text(state_hhs.index[-1],state_hhs[dataset][-1]+state_hhs[dataset][-1]*0.1,\
                '{0:,.0f}'.format(state_hhs[dataset][-1]),color='red')
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
        plt.savefig('%s/%s_%s.png' % (savedir,basicdata[dataset].lower(),state.lower()),bbox_inches='tight')
        plt.close(fig)
        
print('Done')
