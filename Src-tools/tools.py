import sys
import os 
import pandas as pd
import geopandas as gpd
import shapely 
import numpy as np 
from matplotlib import pyplot as plt
from shapely.geometry import Polygon
from sklearn.cluster import AgglomerativeClustering
import multiprocessing
import pdb 
import warnings
#warnings.filterwarnings("error")
import pyproj
import importlib 
from rasterio.warp import calculate_default_transform, reproject, Resampling
import socket
import json 

#homebrwed
#sys.path.append('../src-load/')
#glc = importlib.import_module("load-glc-category")


#######################
def getFeatures(gdf):
    """Function to parse features from GeoDataFrame in such a manner that rasterio wants them"""
    return [ json.loads(gdf.to_json())['features'][ii]['geometry']  for ii in range(len(gdf)) ]


########################
def ensure_dir(f):
    d = os.path.dirname(f)
    if not os.path.exists(d):
        os.makedirs(d)


##########################
def my_read_file(filepath):
    if os.path.isfile(filepath.replace('.geojson','.prj')):
        tmp = gpd.read_file(filepath)
        with open(filepath.replace('.geojson','.prj'),'r') as f:
            lines = f.readlines()
        try:
            tmp.set_crs(crs=lines[0], allow_override=True, inplace=True)
        except: 
            pdb.set_trace()
        return tmp
    else:
        return gpd.read_file(filepath)


##########################
def cpu_count():
    try:
        return int(os.environ['ntask'])
    except:
        print('env variable ntask is not defined')
        sys.exit() 
        #return multiprocessing.cpu_count()

##########################
def cluster_shapes_by_distance(geodf, distance):
    """
    Make groups for all shapes within a defined distance. For a shape to be 
    excluded from a group, it must be greater than the defined distance
    from *all* shapes in the group.
    Distances are calculated using shape centroids.

    Parameters
    ----------
    geodf : data.frame
        A geopandas data.frame of polygons. Should be a projected CRS where the
        unit is in meters. 
    distance : float
        Maximum distance between elements. In meters.

    Returns
    -------
    np.array
        Array of numeric labels assigned to each row in geodf.

    """
    assert geodf.crs.is_projected, 'geodf should be a projected crs with meters as the unit'
    centers = [p.centroid for p in geodf.geometry]
    centers_xy = [[c.x, c.y] for c in centers]
    
    cluster = AgglomerativeClustering(n_clusters=None, 
                                      linkage='single',
                                      metric='euclidean',
                                      distance_threshold=distance)
    cluster.fit(centers_xy)
    
    return cluster.labels_


##########################
def dissolveGeometryWithinBuffer(gdf,bufferSize = 20.):

    gdf['geometry'] = gdf.geometry.apply(lambda g: g.buffer(bufferSize))

    s_ = gpd.GeoDataFrame(geometry=[gdf.unary_union]).explode( index_parts=False ).reset_index( drop=True )

    s_ = s_.geometry.apply(lambda g: g.buffer(-1*bufferSize))

    return s_

##########################
def getDistanceBetweenGdf(gdf1,gdf2):
    return gdf1.geometry.apply(lambda g: gdf2.distance(g))


##########################
def test_getDistanceBetweenGdf():
    df1 = pd.DataFrame(
        {
            "x": [0, 1, 1, 0],
            "y": [0, 0, 1, 1],
            "label": ['1', '1', '1', '1'],
        })

    df2 = pd.DataFrame(
        {
            "x": [3, 4, 4, 3],
            "y": [0, 0, 1, 1],
            "label": ['1', '1', '1', '1'],
        })
    gdf = gpd.GeoDataFrame(index=[1,2],
        geometry=[Polygon(zip(df1['x'],df1['y'])), Polygon(zip(df2['x'],df2['y']))]
        )
    print( getDistanceBetweenGdf(gdf,gdf))

    gdf.plot()
    plt.show()



###########################################################
def reproject_raster(src_band, src_bounds, src_transform, src_crs, dst_crs, resolution=200):
    dst_transform, width, height = calculate_default_transform(
        src_crs,
        dst_crs,
        src_band.shape[1],
        src_band.shape[2],
        *src_bounds,  # unpacks outer boundaries (left, bottom, right, top)
        resolution=resolution
    )
    dst_band = np.zeros([height, width])

    try: 
        return  reproject(
        source=src_band,
        destination=dst_band,
        src_transform=src_transform,
        src_crs=src_crs,
        dst_transform=dst_transform,
        dst_crs=dst_crs,
        dst_nodata=-999,
        resampling=Resampling.nearest)
    except:
        pdb.set_trace()


    
