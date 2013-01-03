import os, re
from glob import glob
import nibabel as ni
import numpy as np
import nipype.interfaces.fsl as fsl
from nipype.interfaces.base import CommandLine
from nipype.utils.filemanip import split_filename
"""
infiles are
<basedir>/<subid>.ica/reg_standard/filtered_func_data.nii.gz
"""


def create_common_mask(infiles, outdir):
    """
    for each file:
    calc std across time
    save to mask

    merge files into 4d brik
    calc voxelwise min across time
    save as maskALL
    """
    nsub = len(infiles)
    dim = ni.load(infiles[0]).get_shape()
    mask = np.zeros((dim[0], dim[1], dim[2],nsub))
    for val, f in enumerate(infiles):
        dat = ni.load(f).get_data()
        dstd = dat.std(axis=3)
        mask[:,:,:,val] = dstd
    minmask = mask.min(axis=3)
    newimg = ni.Nifti1Image(minmask, ni.load(infiles[0]).get_affine())
    outfile = os.path.join(outdir, 'mask.nii.gz')
    newimg.to_filename(outfile)
    return outfile


def get_subid(instr, pattern='B[0-9]{2}-[0-9]{3}'):
    """regexp to find pattern in string
    default pattern = BXX-XXX  X is [0-9]
    """
    m = re.search(pattern, instr)
    try:
        subid = m.group()
    except:
        print pattern, ' not found in ', instr
        subid = None
    return subid

    
def dual_regressions(infiles, melodicIC, mask,desnorm = 1):              
    """
    TODO: keep wrapper, split 3 functions test
    for file in infiles:
    subid
    fsl_glm -i <file> -d <melodicIC> -o <outdir>/dr_stage1_${subid}.txt --demean -m <mask>;\
    fsl_glm -i <file> -d <outdir>/dr_stage1_${subid}.txt  -o <outdir>/dr_stage2_$s --out_z=<outdir>/dr_stage2_${subid}_Z --demean -m $OUTPUT/mask <desnorm>;\
    fslsplit <outdir>/dr_stage2_$s $OUTPUT/dr_stage2_${s}_ic
    """
    startdir = os.getcwd()
    outdir, _ = os.path.split(mask)
    os.chdir(outdir)
    subd = {}
    melodicpth, melodicnme, melodicext = split_filename(melodicIC)
    melodicIC = os.path.join(melodicpth, melodicnme)
    for f in infiles:
        fpth, fnme, fext = split_filename(f)
        f = os.path.join(fpth, fnme)
        subid = get_subid(f)
        tmpout = os.path.join(outdir, 'dr_stage1_%s.txt'%(subid))
        cmd = ' '.join(['fsl_glm -i %s'%(f), '-d %s'%(melodicIC),  '-o %s'%(tmpout), '--demean', '-m %s'%(mask)])
        cout = CommandLine(cmd).run()
        if not cout.runtime.returncode == 0:
            print cout.runtime.stderr
            continue
        tmpout2 = os.path.join(outdir, 'dr_stage2_%s'%(subid))
        tmpout2z = os.path.join(outdir,'dr_stage2_%s_Z'%(subid))
        cmd = ' '.join(['fsl_glm -i %s'%(f), '-d %s'%(tmpout), '-o %s'%(tmpout2), '--out_z=%s'%(tmpout2z),
                        '--demean', '-m %s'%(mask), '%d'%desnorm])
        cout = CommandLine(cmd).run()
        if not cout.runtime.returncode == 0:
            print cmd
            print cout.runtime.stderr
            continue
        outic = os.path.join(outdir, 'dr_stage2_%s_ic'%(subid))
        cmd = ' '.join(['fslsplit', tmpout2, outic])
        cout = CommandLine(cmd).run()
        if not cout.runtime.returncode == 0:
            print cmd
            print cout.runtime.stderr
            continue
        allic = glob('%s*'%(outic))
        allic.sort()
        subd.update({subid: allic})
    os.chdir(startdir)
    return subd
    
    

def merge_components(subd):
    """ for each component
    concat subjects into 4D file
    write subject order to file
    Returns
    -------
    4dfiles : list of component 4d files

    subjectorder : string
        text file holding the order of subjects in 4d component files
    """
    keys = sorted(subd)


    return 4dfiles, subjectorder
    


def sort_maps_randomise(stage2_ics, mask, perms=500):
    """
    design = -1  # just ttest
    permutations = 500
    run this on each subject
    for val, stage2_ic in enumerate(stage2_ics):
    randomise -i stage2_ic -o <outdir>/dr_stage3_ic<val> -m <mask> <design> -n <permutations> -T -V
    fslmerge -t stage2_ic4d stage2_ics*
    remove stage2_ics
    """
    startdir = os.getcwd()
    outdir, _ = os.path.split(mask)
    os.chdir(outdir)
    mask = mask.strip('.nii.gz')
    design = -1

    mergefile = stage2_ics[0].replace('.nii.gz', '_4D.nii.gz')
    cmd = 'fslmerge -t %s '%(mergefile) + ' '.join(stage2_ics)
    cout = CommandLine(cmd).run()
    if not cout.runtime.returncode == 0:
        print cmd
        print cout.runtime.stderr, cout.runtime.stdout
        return
    stage3 = mergefile.replace('stage2', 'stage3')
    cmd = ' '.join(['randomise -i %s'%(mergefile), '-o %s'%(stage3),'%d'%(design),'-m %s'%(mask), '-n %d'%(perms), '-T'])
    cout = CommandLine(cmd).run()
    if not cout.runtime.returncode == 0:
        print cmd
        print cout.runtime.stderr, cout.runtime.stdout
        return cmd
    os.chdir(startdir)

if __name__ == '__main__':

    basedir = '/home/jagust/pib_bac/ica/data/tr189_melodic'
    outdir = os.path.join(basedir, 'ica.gica', 'dual_regress')
    melodicIC = os.path.join(basedir, 'ica.gica','groupmelodic.ica','melodic_IC.nii.gz')
    infiles = glob('%s/B*.ica/reg_standard/filtered_func_data.nii.gz'%(basedir))
    infiles.sort()
    
    #mask = create_common_mask(infiles, outdir)
    mask = basedir + '/ica.gica/dual_regress/mask.nii.gz'
    subd = dual_regressions(infiles, melodicIC, mask)

    for i in range(len(subd[subd.keys()[0]])):
        if i == 0:
            continue
        items = [x[i] for x in sorted(subd.values())]
        cmd = sort_maps_randomise(items, mask, perms=500)
    """
    for sub in sorted(subd):
        st2_ics = subd[sub]
        cmd = sort_maps_randomise(st2_ics,mask, perms=500)
    """
