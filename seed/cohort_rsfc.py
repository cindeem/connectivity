"""
resid_4d = '/home/jagust/pib_bac/ica/data/spm_189/B05-201/func/B05-201_resid.nii.gz'

seed = '/home/jagust/pib_bac/ica/data/spm_189/B05-201/seed_ts/4mm_AndrewsHanna2010_LeftRetroSpl_-14_-52_8.txt'

outdir = '/home/jagust/pib_bac/ica/data/spm_189/B05-201/func/RSFC'

seedname = 'left_retrosplenial'

seed_corr = os.path.join(outdir, '%s_corr.nii.gz'%(seedname))
cmd = '3dfim+ -input %s -ideal_file %s -out Correlation -bucket '%(resid_4d, seed, seed_corr)
os.system(cmd)

seed_z = os.path.join(outdir, '%s_z.nii.gz'%(seedname))
cmd = "3dcalc -a %s -expr 'log((a+1)/(a-1))/2'  -prefix %s"%(seed_corr, seed_z)

# mask
mask_seed_z = os.path.join(outdir, 'mask_%s_z.nii.gz'%(seedname))
maskvol = '/home/jagust/pib_bac/ica/data/spm_189/overlap_mask.nii.gz'
cmd = 'fslmaths %s -mas %s %s'%(seed_z, maskvol, mask_seed_z)
g"""

import os, sys, re
from glob import glob
import argparse
sys.path.insert(0, '/home/jagust/cindeem/CODE/manja')
import preprocess as pp
import numpy as np
from numpy import loadtxt, array
import nibabel as ni

def seed_voxel_corrz(fourd, seed, outdir):
    """ uses numpy, nibabel to calc timeseries correlation
    with seed values, ztransforms and saves to file in outdir"""
    _, seedname, _ = pp.split_filename(seed)
    outfile = os.path.join(outdir, '%s_corrz.nii.gz'%(seedname))
    seedval = np.loadtxt(seed)
    img = ni.load(fourd)
    dat = img.get_data()
    new = np.zeros(dat.shape[:3])
    for i, slice in enumerate(dat):
        for j, part in enumerate(slice):
            res = np.corrcoef(part, seedval)
            new[i,j,:] = res[-1,:-1]
    new = np.arctanh(new)
    new[np.isnan(new)] = 0
    newimg = ni.Nifti1Image(new, img.get_affine())
    newimg.to_filename(outfile)
    return outfile

def seed_voxel_masked_corrz(fourd, seed, maskf, outdir):
    _, seedname, _ = pp.split_filename(seed)
    outfile = os.path.join(outdir, '%s_corrz.nii.gz'%(seedname))
    seedval = np.loadtxt(seed)
    img = ni.load(fourd)
    imgdim = img.get_shape()[:3]
    maskdim = ni.load(maskf).get_shape()
    if not maskdim == imgdim:
        raise ValueError('dimension mismatch, mask: %s, data: %s'%(maskdim, imgdim))
    dat = img.get_data()
    maskdat = ni.load(maskf).get_data()
    mask = maskdat > 0
    masked_dat = dat[mask,:]
    steps = [x * mask.shape[0]/10 for x in range(10)]
    steps.append(-1)
    allres = np.zeros(masked_dat.shape[0])
    for i, stop in enumerate(steps):
        start = steps[i]
        clump = masked_dat[start:s,:]
        tmpres = np.corrcoef(clump, seed)
        allres[start:s] = tmpres[-1,:-1]
    new = np.zeros(dat.shape[:3])
    new[mask] = allres
    newimg = ni.Nifti1Image(new, img.get_affine())
    newimg.to_filename(outfile)
    return outfile




def generate_seed_voxelcorrelation(fourd, seed, outdir):
    _, seedname, _ = pp.split_filename(seed)
    outfile = os.path.join(outdir, '%s_corr.nii.gz'%(seedname))
    cmd = ' '.join(['3dfim+',
                    '-input',
                    fourd,
                    '-ideal_file',
                    seed,
                    '-out',
                    'Correlation', 
                    '-bucket',
                    outfile])
    cout = pp.CommandLine(cmd).run()
    if not cout.runtime.returncode == 0:
        print cout.runtime.stderr
        return None
    return outfile

def ztrans_correl(infile):
    outfile = infile.replace('_corr', '_corrZ')
    cmd = ' '.join(['3dcalc',
                    '-a',
                    infile,
                    '-expr',
                    '"log((a+1)/(a-1))/2"',
                    '-prefix',
                    outfile])
    cout = pp.CommandLine(cmd).run()
    if not cout.runtime.returncode == 0:
        print cout.runtime.stderr
        return None
    return outfile



def find_fixed_frames(datadir, pattern ='auB[0-9]*-*[0-9].nii*' ):
    """ looks in the <slicetime> directory of realigned files and
    check for files with symbolic links (suggesting fixed files)
    returns a list holding framenumbers"""
    allf = glob(os.path.join(datadir, pattern))
    allf.sort()
    islink = [val for val, x in enumerate(allf) if os.path.islink(x)]
    return islink

    
def mask_input_timeseries(timeseries, bad_frames, clobber=True):
    """ When using 3dfim+ if you replace a bad frames value with  '99999'
    it will be ignored in the model

    Inputs
    ------
    timeseries : str
        file holding the timeseries data to correlate
    bad_frames : list
        list of frames to inject 99999 into
    clobber : bool
        if true overwrite initial file, else a new file
        masked_<timeseries> will be created

    Returns
    -------
    outf : str
        file holding the masked timeseries
    """
    precis = get_precision(timeseries)
    dat = loadtxt(timeseries)
    dat[array(bad_frames)] = 99999
    outf = timeseries
    if not clobber:
        pth, nme = os.path.split(timeseries)
        outf = os.path.join(pth, 'masked_%s'%nme)
    format = '%5' + '.%df'%(precis)
    dat.tofile(outf, sep='\n', format = format)
    return outf


def get_precision(infile):
    """ returns the floating precision written to a file
    based on largest number of digits after '.' """
    precision = 0
    for line in open(infile):
        try:
            tmp = len(line.strip('\n').split('.')[-1])
            if tmp > precision:
                precision = tmp
                
        except:
            raise IOError('Unable to guess precision form %s'%line)
        return precision
    
def main(datadir, globstr, seedname, resid, mask=None):    
   
    fullglob = os.path.join(datadir, globstr, seedname)
    allf = sorted(glob(fullglob))
    

    for seed in allf[:]:
        pth, _ = os.path.split(seed)
        rsfc, exists = pp.make_dir(pth, 'RSFC')
        # get residual fourd vol
        
        subdir, _ = os.path.split(pth)
        globstr = os.path.join(subdir, resid)
        fourd = glob(globstr)
        if not len(fourd) >= 1:
            print 'residual missing?: %s '%(globstr)
            continue
        fourd = fourd[0]
        #slicetimedir = os.path.join(subdir, 'func','slicetime')
        #fixed = find_fixed_frames(slicetimedir)
        #if len(fixed) > 0:
        #    seed = mask_input_timeseries(seed, fixed, clobber=False)
        if mask is None:
            zcorr =  seed_voxel_corrz(fourd, seed, rsfc)  
        else:
            zcorr = seed_voxel_masked_corrz(fourd, seed, mask, rsfc)
        #corr_file = generate_seed_voxelcorrelation(fourd, seed, rsfc)
        #zcorr = ztrans_correl(corr_file)
        print zcorr

if __name__ == '__main__':

    parser = argparse.ArgumentParser(
            description = """ Use timecourse from seed in txt file
            to calculate whole brain rsfc"""
            )
    parser.add_argument('datadir', type=str, nargs=1,
            help = 'Directory holding project data')
    parser.add_argument('globstr', type=str, nargs=1,
            default='B*/seed_ts', 
            help='glob to get seed dir (default= B*/seed_ts)')
    parser.add_argument('seedname', type = str, nargs=1,
            help='name of seed txt file (eg. ppc.txt )')
    parser.add_argument('-resid', type = str, nargs=1, 
            default='B*resid_june2013.nii*',
            help='glob for resid in subject dir (default = B*resid_june2013.nii*)')
    parser.add_argument('-mask', type = str, default = None,
            help = 'Mask to restrict region of correlation')
    if len(sys.argv) ==1:
        parser.print_help()
    else:
        args = parser.parse_args()
        print args
        main(args.datadir[0], args.globstr[0], args.seedname[0], 
             args.resid, args.mask)

