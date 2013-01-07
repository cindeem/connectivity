import re
import numpy as np
from scipy.stats import pearsonr

def calc_eta(a,b, getr = False):
    """
    Cohen's eta calculates the similarity between a and b
    on a pointwise basis

    Shape a must equal shape b

    if getr also returns pearson correlation between a,b

    Returns
    -------
    cohen_eta (float):
       0 means dissimilar, 1 means same

    pearsonsr (float) if getr is true
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


def get_subid(infile):
    """ parse filepath string like this:
    /home/to/data/B06-235/seed_ts_dmn_march2012/RSFC/3_corrZ.nii.gz
    with regular expression [B][0-9]{2}\-[0-9]{3}
    to get subject ID  B06-235
    """
    m = re.search('[B][0-9]{2}\-[0-9]{3}',infile)
    if m is None:
        print 'subid not found in %s'%infile
        return None
    else:
        return m.group(0)
     



if __name__ == '__main__':
    print 'cohen eta'
    eta = calc_eta(np.random.rand(10), np.random.rand(10))
    (eta,r) = calc_eta(np.random.rand(10), np.random.rand(10), getr = True)
