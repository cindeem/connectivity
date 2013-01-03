import os, shutil
from datetime import datetime as dtime
from glob import glob
import tempfile
from nipype.interfaces.base import CommandLine
from nipype.interfaces.fsl import ApplyWarp, ImageMaths, ImageStats



def applywarp(infile, ref, regdir, outname):
    warp = os.path.join(regdir, 'highres2standard_warp.nii.gz')
    premat = os.path.join(regdir, 'example_func2highres.mat')
    if not os.path.isfile(warp):
        print 'no warp found: ', warp
        return None
    if not os.path.isfile(premat):
        print 'no premat found ', premat
        return None
    startdir = os.getcwd()
    pth, nme = os.path.split(infile)
    os.chdir(pth)
    mywarp = ApplyWarp()
    mywarp.inputs.in_file = infile
    mywarp.inputs.ref_file = ref
    mywarp.inputs.field_file = warp
    mywarp.inputs.premat = premat
    warpout = mywarp.run()
    os.chdir(startdir)
    if warpout.runtime.returncode == 0:
        #apply warp successful
        warped = warpout.outputs.out_file
        return warped
    else:
        print warpout.runtime.stderr
        return None


if __name__ == '__main__':


    template = '/home/jagust/pib_bac/ica/data/templates/MNI152_T1_3mm_brain.nii.gz'
    allsubs = glob('/home/jagust/pib_bac/ica/data/fromBeth/B*')

    outdir = '/home/jagust/pib_bac/ica/data/tr189_melodic'

    for item in allsubs:
        subid = item.split('/')[-1]
        resting = glob('%s/4d*.feat/filtered_func_data.nii.gz'%(item))[0]
        restdir, _ = os.path.split(resting)
        regdir = os.path.join(restdir, 'reg')
        outfile = os.path.join(outdir, '%s_rest_3mm.nii.gz'%(subid))
        warped = applywarp(resting, template, regdir, outfile)
        
