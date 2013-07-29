
import os
import sys
import argparse
import scipy.special as sspec
from scipy import interpolate
from scipy.signal import cubic

def spline_dtrend(data, tr = 2):
    """use spline to detrend data"""
    y = data
    x = arange(len(data))
    xx = np.arange(0, len(data), 2)
    tck = interpolate.splrep(xx, y, s=0)
    ynew = interpolate.splev(xx,tck,der=0)
    return data - ynew

def demean(data):
    """ remove mean value from a dataset"""
    return data - data.mean()


