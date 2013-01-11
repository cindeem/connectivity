import os, sys
from glob import glob
sys.path.insert(0, '/home/jagust/jelman/rsfmri_ica/code/connectivity/ica')
import python_dual_regress as pydr

if __name__ == '__main__':

    #location of ICA data
    #######################
    basedir = '/home/jagust/jelman/rsfmri_ica/data/Test'
    # output directory
    outdir = os.path.join(basedir, 'OldICA_IC25_ecat.gica', 'dual_regress')
    if os.path.isdir(outdir)==False:
        os.mkdir(outdir)      
    else:
        #If outdir exists, rename existing dir with timestamp appended
        mtime = os.path.getmtime(outdir)
        tmestamp = datetime.datetime.fromtimestamp(mtime).strftime('%Y-%m-%d_%H-%M-%S')
        newdir = '_'.join([outdir,tmestamp])
        os.rename(outdir,newdir)
        os.mkdir(outdir)
        print outdir, 'exists, moving to ', newdir
        
    # location for 4D template components (eg melodic_ICA, laird_4D)
    template = os.path.join(basedir, 'OldICA_IC25_ecat.gica',
                             'groupmelodic.ica','melodic_IC.nii.gz')

    # look for subjects already registered filtered func ica data
    globstr = os.path.join(basedir, #data directory
                            'B*', #subject directory
                            'func', #functional data directory
                            'B*.ica', # subject speccific
                            'reg_standard', # registered to standard
                            'filtered_func_data.nii.gz') # data
    infiles = glob(globstr)
    infiles.sort()

    # get mask from groupica
    #######################
    mask = os.path.join(basedir,
                        'OldICA_IC25_ecat.gica',
                        'mask.nii.gz')

    ### RUN DUAL REGRESSION
    #######################
    subd = {}
    for tmpf in infiles: #subject-wise
        subid = pydr.get_subid(tmpf)
        txtf = pydr.template_timeseries_sub(tmpf, template, mask, outdir)
        ## If you want to add movement params & spike regressors to stage2 of model
        ## mvtfile = [confound file] and change from None below
        mvtfile = os.path.join(basedir,
                            subid,
                            'func',
                            'confound_regressors.txt') #Name of confound file
        
        allic = pydr.sub_spatial_map(tmpf, txtf, mask, outdir,
                                     desnorm=1, mvt=mvtfile)
        
        subd.update({subid:allic})
    # concat ics across subjects
    #######################
    for cn, item in enumerate(allic): # search for all subjects based on last
        datadir, ic = os.path.split(item)
        subid = get_subid(item)
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
