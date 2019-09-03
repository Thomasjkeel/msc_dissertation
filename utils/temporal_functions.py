import pandas as pd
import geopandas as gpd
import statsmodels
import matplotlib.pyplot as plt
import numpy as np


def group_var_24hr(data, var, column='starttime', time_grp=1 ,units='h', purpose=True):
    """
    Groups the data by purpose or mode for a given time period and then takes the average across a 24-day.
    Note: doesn't divide the data into week/weekends
    
    Paramaters:
    -----------
    data : geopandas.GeoDataFrame
        contains the MTL-Trajet information
    var : string
        the purpose or mode of the trip entered by user
    columns : string
        column containing the 
    time : int or string
        time to group each day into
    units : string
        units for the time (i.e. h or min)
        
    """
    unit_vals = {} # dictionary for holding the mean value at each time unit
    
    try:
        column = str(column)
        time_grp = int(time_grp)
        assert column in data.columns, "\'%s\' not found as a column in data" % column
        if purpose:
            assert 'purpose' in data.columns, "\'purpose\' not found as a column in data"
        else:
            assert 'mode' in data.columns, "\'mode\' not found as a column in data"
    except:
        raise TypeError ("invalid input")
    
    freq_units = str(time_grp)+units
    
    if purpose:
        data = data.set_index(column).groupby([gpd.pd.Grouper(freq=freq_units), 'purpose']).agg({'id_trip':'count'})
    else:
        data = data.set_index(column).groupby([gpd.pd.Grouper(freq=freq_units), 'mode']).agg({'id_trip':'count'})
    data.reset_index(inplace=True)
    data.set_index(column, inplace=True)
    
    if units == 'h':
        num = int(np.floor(24 / int(time_grp)))
#         periods = np.arange(int(24/num)-1,24, time_grp)
        ind_time_units = data.index.hour
    elif units == 'min':
        num = int(np.floor((1440) / int(time_grp)))
#         periods = np.arange(int(1440/num)-1,1440, time_grp)
        ind_time_units = data.index.minute
    else:
        return print("please enter appropriate units: \'h\' or \'min\'")

    for tm in data.index.hour.unique():
        if purpose:
            tm_mean = data.loc[(ind_time_units == tm) & (data['purpose'] == var)]
        else:
            tm_mean = data.loc[(ind_time_units == tm) & (data['mode'] == var)]
        tm_mean = tm_mean.mean().values[0]
        unit_vals[tm] = tm_mean
    return unit_vals


def group_var_calendar(data, var=None, column='starttime', purpose=True):
    """
    Groups the data by purpose or mode across the week for each hour
    
    Paramaters:
    -----------
    data : geopandas.GeoDataFrame
        contains the MTL-Trajet information
    var : string
        i.e. 'purpose' or 'mode' of the trip
    columns : string
        column containing the datetime variable to group by
    time : int or string
        time to group each day into
    units : string
        units for the time (i.e. h or min)
        
    """
    ordered_days = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday', 'Sunday']
    ## groupby all modes 
    if purpose:
        data = data.set_index(column).groupby([gpd.pd.Grouper(freq='1h'), 'purpose']).agg({'id_trip':'count'})
    else:
        data = data.set_index(column).groupby([gpd.pd.Grouper(freq='1h'), 'mode']).agg({'id_trip':'count'})
    data.reset_index(inplace=True)
    week_hours = {}
    
    for hr in range(0, 24):
        # check if var has been stated or just do total
        if var:
           
            if purpose:
                assert var in data['purpose'].unique(), "var: \'%s\' is not in the purpose column of the dataframe" % (var)
                hr_data = data.loc[(data.starttime.apply(lambda tm: tm.hour == hr)) & (data['purpose'] == var)]
            else:
                assert var in data['mode'].unique(), "var: \'%s\' is not in the mode column of the dataframe" % (var)
                hr_data = data.loc[(data.starttime.apply(lambda tm: tm.hour == hr)) & (data['mode'] == var)] 
        else:
            print("here")
            hr_data = data.loc[data.starttime.apply(lambda tm: tm.hour == hr)]
            
        hr_data = hr_data.groupby(hr_data.starttime.dt.weekday_name).mean().reindex(ordered_days) # re-order index by day
        week_hours[hr] = hr_data.values
    return week_hours



def ts_diagnostics(y, lags=None, title=''):
    '''
    Calculate acf, pacf, qq plot and Augmented Dickey Fuller test for a given time series
    FROM ONLINE SOMEWHERE (STACK OVERFLOW)
    '''
    if not isinstance(y, pd.Series):
        y = pd.Series(y)

    # weekly moving averages (5 day window because of workdays)
    rolling_mean = pd.rolling_mean(y, window=12)
    rolling_std = pd.rolling_std(y, window=12)

    fig = plt.figure(figsize=(14, 12))
    layout = (3, 2)
    ts_ax = plt.subplot2grid(layout, (0, 0), colspan=2)
    acf_ax = plt.subplot2grid(layout, (1, 0))
    pacf_ax = plt.subplot2grid(layout, (1, 1))
    qq_ax = plt.subplot2grid(layout, (2, 0))
    hist_ax = plt.subplot2grid(layout, (2, 1))

    # time series plot
    y.plot(ax=ts_ax)
    rolling_mean.plot(ax=ts_ax, color='crimson');
    rolling_std.plot(ax=ts_ax, color='darkslateblue');
    plt.legend(loc='best')
    ts_ax.set_title(title, fontsize=24);

    # acf and pacf
    statsmodels.graphics.tsaplots.plot_acf(y, lags=lags, ax=acf_ax, alpha=0.5)
    statsmodels.graphics.tsaplots.plot_pacf(y, lags=lags, ax=pacf_ax, alpha=0.5)

    # qq plot
    statsmodels.graphics.gofplots.qqplot(y, line='s', ax=qq_ax)
    qq_ax.set_title('QQ Plot')

    # hist plot
    y.plot(ax=hist_ax, kind='hist', bins=25);
    hist_ax.set_title('Histogram');
    plt.tight_layout();
    #     plt.savefig('./img/{}.png'.format(filename))
    plt.show()

    # perform Augmented Dickey Fuller test
    print('Results of Dickey-Fuller test:')
    dftest = statsmodels.tsa.stattools.adfuller(y, autolag='AIC')
    dfoutput = pd.Series(dftest[0:4], index=['test statistic', 'p-value', '# of lags', '# of observations'])
    for key, value in dftest[4].items():
        dfoutput['Critical Value (%s)' % key] = value
    print(dfoutput)
    return
