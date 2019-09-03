import shapely
import numpy as np
import geopandas as gpd
import matplotlib.pyplot as plt

def change_crs(data, crs, data_name):
    """
    changes the crs of the

    Parameters
    ----------
    data : geopandas.geodataframe.GeoDataFrame
        dataframe that is going
    crs : dictionary
        in the format {'init' :'epsg:????'}
    data_name : string
        name of the dataframe

    Returns
    -------
    grouped_data :geopandas.geodataframe.GeoDataFrame
    """
    data_name = str(data_name)
    if data.crs != crs:
        print("translating {0} data".format(data_name))
        data = data.to_crs(crs=crs)
    else:
        print("correct crs for {0}".format(data_name))
    return data


def get_point_from_linestring(geom_row, X=0, behaviour='last'):
    """
    Function for extracting the Xth point of a linestring.
    Default X is the first point, default behaviour is the last

    Parameters
    ----------
    geom_row : shapely.geometry.linestring.LineString or shapely.geometry.multilinestring.MultiLineString
        A geometry row containing the route

    X : int or float
        The index of the point. Note: rounded if float

    behaviour:
        The behaviour if the index given doesn't exist
        args={'last': 'return the last available value i.e. -1', 'ignore':'ignore the row and return None'}

    Returns
    -------
    float
        lat, lng: tuple of floats
    """

    lat = None
    lng = None
    try:
        X = round(X)
    except Exception as e:
        raise TypeError("Please enter a number for the index of the point within the linestring (X)")

    if behaviour in ['last', 'ignore']:
        pass
    else:
        behaviour = 'last'

    if type(geom_row) == shapely.geometry.multilinestring.MultiLineString:
        total_linestrings = len(geom_row)
        lengths = {}
        total_len = 0
        for line in range(total_linestrings):
            len_line = len(geom_row[line].xy[0])
            lengths[line] = len_line
            total_len += len_line
        if X > total_len and behaviour == 'ignore':
            return lng, lat
        elif X > total_len and behaviour == 'last' or X == -1:
            lat = geom_row[-1].xy[1][-1]
            lng = geom_row[-1].xy[0][-1]
        else:
            total = 0
            for key, val in lengths.items():
                # find the location of X within the dictionary by looking if its in a given key
                total += val
                if total >= X:
                    ind_key = key
                    dict_ind = (val - (total - X)) - 1  # minus 1 as Python has a base-0 index
                    break
            lat = geom_row[ind_key].xy[1][dict_ind]
            lng = geom_row[ind_key].xy[0][dict_ind]

    elif type(geom_row) == shapely.geometry.linestring.LineString:
        len_line = len(geom_row.xy)
        lng = geom_row.xy[0][X]
        lat = geom_row.xy[1][X]

    return lng, lat


def remove_third_dimension(geom):
    # from: https://gis.stackexchange.com/questions/67210/convert-3d-wkt-to-2d-shapely-geometry

    if geom.is_empty:
        return geom

    if isinstance(geom, shapely.geometry.Polygon):
        exterior = geom.exterior
        new_exterior = remove_third_dimension(exterior)

        interiors = geom.interiors
        new_interiors = []
        for int in interiors:
            new_interiors.append(remove_third_dimension(int))

        return shapely.geometry.Polygon(new_exterior, new_interiors)

    elif isinstance(geom, shapely.geometry.LinearRing):
        return shapely.geometry.LinearRing([xy[0:2] for xy in list(geom.coords)])

    elif isinstance(geom, shapely.geometry.LineString):
        return shapely.geometry.LineString([xy[0:2] for xy in list(geom.coords)])

    elif isinstance(geom, shapely.geometry.Point):
        return shapely.geometry.Point([xy[0:2] for xy in list(geom.coords)])

    elif isinstance(geom, shapely.geometry.MultiPoint):
        points = list(geom.geoms)
        new_points = []
        for point in points:
            new_points.append(remove_third_dimension(point))

        return shapely.geometry.MultiPoint(new_points)

    elif isinstance(geom, shapely.geometry.MultiLineString):
        lines = list(geom.geoms)
        new_lines = []
        for line in lines:
            new_lines.append(remove_third_dimension(line))

        return shapely.geometry.MultiLineString(new_lines)

    elif isinstance(geom, shapely.geometry.MultiPolygon):
        pols = list(geom.geoms)

        new_pols = []
        for pol in pols:
            new_pols.append(remove_third_dimension(pol))

        return shapely.geometry.MultiPolygon(new_pols)

    elif isinstance(geom, shapely.geometry.GeometryCollection):
        geoms = list(geom.geoms)

        new_geoms = []
        for geom in geoms:
            new_geoms.append(remove_third_dimension(geom))

        return shapely.geometry.GeometryCollection(new_geoms)
    
    
def plot_counts(data, mtl_dissemination_areas, var, purpose=True, cmap='Reds', return_df=False, plot=True):
    """
    function for plotting a map of counts of a variable
    """
    if purpose:
        assert var in data['purpose'].unique(), "var: \'%s\' is not in the purpose column of the dataframe" % (var)
        joined_data = gpd.sjoin(data.loc[data['purpose'] == var], mtl_dissemination_areas)
    else:
        assert var in data['mode'].unique(), "var: \'%s\' is not in the mode column of the dataframe" % (var)
        joined_data = gpd.sjoin(data.loc[data['mode'] == var], mtl_dissemination_areas)        
        
    mtl_dissemination_areas['freq_dissem_counts'] = mtl_dissemination_areas.apply(lambda row: joined_data.DAUID.value_counts()[row.DAUID] if row.DAUID in joined_data.DAUID.unique() else 0, axis=1)
    
    if plot:
        fig, ax = plt.subplots(1, figsize=(12,10))
        mtl_dissemination_areas.plot('freq_dissem_counts', linewidth=.1, edgecolor='0.5', legend=True, cmap=cmap, ax=ax)
        plt.title(var)
    
    if return_df:
        return mtl_dissemination_areas
    
    
def get_intersecting_dissemination_ids(cross_section, dissemination_areas):
    """
        takes a spatial join of the the montreal dissemination areas and a route
        and returns all the ids that the route passes through
    
    -------
    returns
    -------
    
    """
    assert 'DAUID' in cross_section.columns 
    dissem_arr = dissemination_areas.loc[dissemination_areas['DAUID'].isin(np.unique(cross_section['DAUID'].values))].DAUID.unique()
    reg_arr = dissemination_areas.loc[dissemination_areas['DAUID'].isin(np.unique(cross_section['DAUID'].values))].CSDUID.unique()
#     code_arr = dissemination_areas.loc[dissemination_areas['DAUID'].isin(np.unique(cross_section['DAUID'].values))].CODEID.unique()


    return list(dissem_arr), list(reg_arr)