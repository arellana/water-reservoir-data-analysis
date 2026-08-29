import numpy as np
import matplotlib.pyplot as plt
from rasterio.plot import show
import rasterio

def nequalize(array,p=5,nodata=0):
    #If the image is a single band: (height, width) simply compute the percentile and normalize
    if len(array.shape)==2:
        vmin=np.percentile(array[array!=nodata],p)
        vmax=np.percentile(array[array!=nodata],100-p)
        eq_array = (array-vmin)/(vmax-vmin)
        eq_array[eq_array>1]=1
        eq_array[eq_array<0]=0
    #If the image has multiple bands: (number of bands, height, width), do the above but for each band separately
    elif len(array.shape)==3:
        eq_array = np.empty_like(array, dtype=float)
        for i in range(array.shape[0]):
            eq_array[i]=nequalize(array[i], p=p, nodata=nodata)
    return eq_array

def plot_rgb(array, band_list , p = 0, nodata = None, figsize = (12,6), title = None):
    '''
    This function takes as input parameters the array to be plotted,
    a list of indices corresponding to the bands we want to use,
    in the order they must be in (e.g.: [1,2,3]), and an optional
    parameter p, the equalization percentile.

    By default it also sets a figure size of (12,6), which can also be modified.

    Returns only a plot, does not modify the original array.
    Note: array must be a matrix with these input dimensions: [bands, rows, columns]
    '''
    if not title:
        title = f'Combination {band_list} \n (percentile {p}%)'

    img = nequalize(array[band_list], p=p, nodata=nodata)
    plt.figure(figsize = figsize)
    plt.title(title , size = 20)
    show(img)
    plt.show()

#Discards nodata values, treating them as 0 by default, and normalizes by the reflectance factor
def delNone(array, nodata = 0, factor=10000):
    return array[array!=nodata]/factor

def guardar_GTiff(fn, crs, transform, mat, meta=None, nodata=None, bandnames=[]):
    if len(mat.shape)==2:
        count=1
    else:
        count=mat.shape[0]

    if not meta:
        meta = {}

    meta['driver'] = 'GTiff'
    meta['height'] = mat.shape[-2]
    meta['width'] = mat.shape[-1]
    meta['count'] = count
    meta['crs'] = crs
    meta['transform'] = transform

    if 'dtype' not in meta: #if no datatype is specified, use float32
        meta['dtype'] = np.float32


    if nodata==None:
        pass
    else:
        meta['nodata'] = nodata

    with rasterio.open(fn, 'w', **meta) as dst:
        if count==1: #it's a 2D array, save it
            dst.write(mat.astype(meta['dtype']), 1)
            if bandnames:
                dst.set_band_description(1, bandnames[0])
        else: #it's a 3D array, save each band
            for b in range(count):
                dst.write(mat[b].astype(meta['dtype']), b+1)
            for b,bandname in enumerate(bandnames):
                dst.set_band_description(b+1, bandname)#
