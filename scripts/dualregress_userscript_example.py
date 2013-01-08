import os, sys
from glob import glob
sys.path.insert(0, '/home/jagust/cindeem/CODE/connectivity/ica')
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
    subd = {}
    for tmpf in infiles: #subject-wise
        subid = get_subid(tmpf)
        txtf = pydr.template_timeseries_sub(tmpf, template, mask, outdir)
        ## If you want to add movement params to stage2 of model
        ## vxt = [movementfile] andd change from None below
        ## globstr find movmenet relative to filtered_func (template space)
        
        allic = pydr.sub_spatial_map(tmpf, txtf, mask, outdir,
                                     desnorm=1, vxt=None)
        
        subd.update({subid:allic})
    # concat ics across subjects
    #######################
    for cn, item in enumerate(allic): # search for all subjects based on last
        datadir, ic = os.path.split(item)
        subid = find_subid(item)
        globstr = ic.replace(subid, '*')
        4dfile, subject_order = pydr.merge_components(datadir,
                                                      globstr = globstr)
        outfile = os.path.join(outdir, 'subject_order_%02d'%cn)
        with open(outfile, 'w+') as fid: 
            fid.write('\n'.join(subject_order))
        
        
    """randomise stage3
                    
    for i in range(len(subd[subd.keys()[0]])):
        if i == 0:
            continue
        items = [x[i] for x in sorted(subd.values())]
        cmd = sort_maps_randomise(items, mask, perms=500)

    """
