import os, sys
from glob import glob
sys.path.insert(0, '/home/jagust/cindeem/CODE/dualregression')
import python_dual_regression as pydr

if __name__ == '__main__':

    #location of ICA data
    #######################
    basedir = '/home/jagust/pib_bac/ica/data/tr189_melodic'
    # output directory
    outdir = os.path.join(basedir, 'ica.gica', 'dual_regress')
    # location for 4D template components (eg melodic_ICA, laird_4D)
    melodicIC = os.path.join(basedir, 'ica.gica',
                             'groupmelodic.ica','melodic_IC.nii.gz')

    # look for subjects already registered filtered func ica data
    globstr = os.path.join(basedir, #data directory
                           'B*.ica', # subject speccific
                           'reg_standard', # registered to standard
                           'filtered_func_data.nii.gz') # data
    infiles = glob(globstr)
    infiles.sort()

    # get mask from groupica
    #######################
    mask = os.path.join(basedir,
                        '/ica.gica/dual_regress/mask.nii.gz')

    ### RUN DUAL REGRESSION
    #######################
    subd = pydr.dual_regressions(infiles, melodicIC, mask)

    # concat ics across subjects
    #######################
    pydr.merge_components(subd)

    """randomise stage3
                    
    for i in range(len(subd[subd.keys()[0]])):
        if i == 0:
            continue
        items = [x[i] for x in sorted(subd.values())]
        cmd = sort_maps_randomise(items, mask, perms=500)

    for sub in sorted(subd):
        st2_ics = subd[sub]
        cmd = sort_maps_randomise(st2_ics,mask, perms=500)
    """
