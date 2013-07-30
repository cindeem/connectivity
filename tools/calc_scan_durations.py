
import os
import sys
import argparse
import numpy as np
import scipy.special as sspec
from scipy import interpolate
from scipy.signal import cubic


def spline_dtrend(data, tr = 2):
    """use spline to detrend data"""
    ## need to subsample timepoints
    # for accurate low freq detrending
    y = data
    x = np.arange(len(data))
    xx = np.arange(0, len(data), tr)
    tck = interpolate.splrep(xx, y, s=0)
    ynew = interpolate.splev(xx,tck,der=0)
    res = data - ynew
    return res

def demean(data):
    """ remove mean value from a dataset"""
    return data - data.mean()


