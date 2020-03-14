import sys
import pandas as pd
# import requests
import pymongo

from datetime import datetime,timedelta
sys.path.append('/projects/utilities/prod')
import tcfutil as utils
import seaborn as sns

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()
# import incentive_lib as utils

def main():
    st=datetime.utcnow().timestamp()
    ex_coll=get_db('zs5_mongo','sensor')['freezer']
    in_list=list(ex_coll.find({}, {'_id': False}))
    df=pd.DataFrame(in_list)
    utils.print_df(df)
    plot(df)
    # plot(df)
    utils.print_time('Total time',st)


def plot(fig_df):
    plt.rcParams["font.size"] = '12'
    fig = plt.figure(figsize=(10, 6))
    # ax = fig.add_subplot(111)
    sns.scatterplot('x'='move_ts','y'='roll','data'=fig_df)
    # ax.plot(fig_df.capacity, label='Capacity',c='k')
    # ax.plot(fig_df.mean_production, label='Monthly mean production',c='g')
    # ax.plot(fig_df.max_production, label='Monthly max production',c='r')
    #
    # ax.set_ylabel('GW')
    # ax.set_ylim(0,35)
    # ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    # ax.grid()
    # plt.legend(loc='upper left')
    # plt.savefig('German_gas-fired.png')
    plt.show()

def capacities():
    url='https://www.energy-charts.de/power_inst/p_inst_year.json'
    indata_json = requests.get(url).json()
    out_list=[]
    for idx in range(len(indata_json)):
        ser_name=indata_json[idx]['key'][0]['en']
        ser_values=indata_json[idx]['values']
        for ser_value in ser_values:
            if ser_name == 'Gas':
                year=ser_value[0]
                yeardate=datetime.strptime(str(ser_value[0]), '%Y')
                obs={'type':ser_name,'date':yeardate,'value':ser_value[1]}
                # print(obs)
                out_list.append(obs)
    out_list.append({'type': 'Gas', 'date': datetime(2020, 1, 1, 0, 0), 'value': 29.85})
    df = pd.DataFrame(out_list)
    df=df[['date','value']]
    df=df.set_index('date',inplace=False)

    df=df.resample('M').ffill()
    df=df['2011':'2019']
    df = df.rename(columns={'value': 'capacity'})

    return df



def production(end_year):
    years=[str(year) for year in range(2010,end_year+1,1)]

    out_list=[]
    for year in years:
        baseurl='https://www.energy-charts.de/power/year_'
        url=''.join([baseurl,year,'.json'])
        print(url)
        indata_json = requests.get(url).json()
        for idx in range(1,len(indata_json)-1):
            ser_name=indata_json[idx]['key'][0]['en']
            ser_values=indata_json[idx]['values']
            for ser_value in ser_values:
                if ser_name =='Gas':
                    obs={'type':ser_name,'ts':ser_value[0]/1000,'value':ser_value[1],'year':datetime.utcfromtimestamp(ser_value[0]/1000).year,
                         'date':datetime.utcfromtimestamp(ser_value[0]/1000)}
                    out_list.append(obs)
    df = pd.DataFrame(out_list)
    df=df[['value','date']]
    df.set_index('date',inplace=True)
    df_mean=df.resample('M').mean()
    df_mean = df_mean.rename(columns={'value': 'mean_production'})
    df_max=df.resample('M').max()
    df_max = df_max.rename(columns={'value': 'max_production'})
    df=df_mean.join(df_max)
    df=df['2011':'2019']
    return df


def get_db(server, db):
    if server == 'zs5_mongo':
        client = pymongo.MongoClient('192.168.1.201', 27017, username='torben', password='Mantra0099')
    db = client[db]
    return db



if __name__ == "__main__":
    main()
