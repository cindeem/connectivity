# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:
import os
from glob import glob
import numpy as np
import nibabel as ni
from scipy.ndimage import affine_transform
from scipy.stats import pearsonr

def reslice_data(img, change_dat, change_aff):
    """ reslices data in space_define_file to matrix of
    resample_file
    Parameters
    ----------
    img  :  nibabel image of space defining image
    change_dat : array if data to resample
    change_aff : 4X4 array defining mapping of change_dat to world space

    Returns
    -------
    data : ndarray of data in change_dat (with corresponding affine
    change_aff)  sliced to shape defined by img (shape and affine)
    """

    T = np.eye(4)
    
    Tv = np.dot(np.linalg.inv(change_aff), 
                np.dot(T, img.get_affine()))
    data = affine_transform(change_dat.squeeze(), 
                            Tv[0:3,0:3], 
                            offset=Tv[0:3,3], 
                            output_shape = img.get_shape()[:3],
                            order=0,mode = 'nearest')

    return  data
        
def get_graymask(infile, threshold=.2):
    """ opens graymask
    thresholds at threshold (default .2), binarizes
    return new nibabel image (not saved)
    """
    img = ni.load(infile)
    dat = img.get_data()
    dat[dat < threshold] = 0
    dat[dat >= threshold] = 1
    newimg = ni.Nifti1Image(dat, img.get_affine(),  ni.Nifti1Header())
    return newimg

def calc_eta(a, b, getr = False):
    """
    Cohen's eta calculates the similarity between a and b
    on a pointwise basis

    Shape a must equal shape b

    if getr also returns pearson correlation between a,b

    Parameters
    ----------
    a : array
        template network
    b : array
        comparison network
    getr : bool
        flag to also return pearson R (default False)

    Returns
    -------
    cohen_eta (float):
       0 means dissimilar, 1 means same

    pearsonsr (float) if getr is True
    """
    a = a.flatten()
    b = b.flatten()
    if not a.shape == b.shape:
        raise IOError("shape mismatch a(%d) , b(%d)"%(a.shape[0],
                                                      b.shape[0]))
    ab = np.empty((2,a.shape[0]))
    ab[0,:] = a
    ab[1,:] = b
    M = ab.mean()
    mi = ab.mean(0)
    SSW = (a-mi)**2 + (b-mi)**2
    SST = (a-M) **2  + (b-M)**2
    eta = 1 - (SSW.sum() / SST.sum())

    if getr:
        outr = pearsonr(a,b)
        return (eta, outr)
    else:
        return eta



def calc_gof(input, template, mask):
    """
    Calc Goodness of Fit or
    (meanz of voxels in network) - (meanz of voxels outside network)
    
    Parameters
    ----------
    input : array
        array unthresholded z-transfomred network you want to match
    template : binary array
        array holding the network you want to match
    mask : array
        array holding a mask to restrict voxels for comparison

    Returns
    -------
    gof : float
        mean of network_zvals - mean non-network zvals

    Notes
    -----
    input, template and mask must all have same dimensions
    
    """
    network = np.logical_and(template > 0, mask>0)
    non_network = np.logical_and(template == 0 , mask > 0)
    netz = input[network]
    nonnetz =  input[non_network]
    gof = netz.mean() - nonnetz.mean()
    return gof


def get_template_networks(metaica, thresh=0):
    """
    load a 4D image of template networks,
    threshold at thresh (if necessary, default 0)
    """
    img = ni.load(metaica)
    dat  = img.get_data()
    dat[dat < thresh] = 0
    newimg = ni.Nifti1Image(dat, img.get_affine(), ni.Nifti1Header())
    return newimg


def calc_grecious_connectome_gof(connectome_img, grecious_dict):
    """
    connectome_img : 4d nibabel image
    grecious_dict : dict of files for each network {name:file}
    mask = mask defined on template
    for each connectome network, calc GOF with Grecios defined networks
    """
    grecios_nets = sorted(grecious_dict.keys())

    dat = connectome_img.get_data()
    x,y,z,vols = dat.shape
    gofd = {}
    for i in range(vols):
        slice = dat[:,:,:,i]
        tmpgof = []
        
        for cmptn, (name, file) in enumerate(sorted(grecious_dict.items())):
            netimg = ni.load(file)
            netdat = netimg.get_data()
            network =  netdat > 0
            non_network = np.logical_and(netdat <= 0 ,
                                         slice >0)
            netz = slice[network]
            nonnetz =  slice[non_network]
            gof = netz.mean() #- nonnetz.mean()
            tmpgof.append([cmptn,gof])
        
        tmpgof = np.array(tmpgof)
        tmpgof = tmpgof[tmpgof[:,1].argsort(),]
        print tmpgof, '\n'
        gofd[i] = [[grecios_nets[int(tmpgof[-1,0])],tmpgof[-1,1]],
                   [grecios_nets[int(tmpgof[-2,0])],tmpgof[-2,1]]]
    
    return gofd       
    

if __name__ == '__main__':

  pass
