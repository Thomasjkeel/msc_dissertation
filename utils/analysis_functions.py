def group_purpose(data, travel_mode, col_order=('cafe', 'education', 'health', 'leisure', 'not_available', 'other', 'pick_up_a_person', 'returning_home', 'shops', 'work')):
    """
    groups data by defined group also fills in missing columns

    Parameters
    ----------
    data : pandas.core.dataframe.DataFrame
        dataframe
    travel_mode : string
        selected travel mode
    col_order : list
        order of the columns

    Returns
    -------
    grouped_data : pandas.core.series.Series
    """
    grouped_data = data.groupby(['mode', 'purpose']).count()['id_trip'][travel_mode]
    total_data = grouped_data.sum()
    print("total data points for '%s': %s" % (travel_mode, total_data))
    grouped_data = grouped_data / grouped_data.sum()
    return grouped_data.reindex(col_order).fillna(0)
