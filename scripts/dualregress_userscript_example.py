import os, sys
from glob import glob
sys.path.insert(0, '/home/jagust/jelman/rsfmri_ica/code/connectivity/ica')
import python_dual_regress as pydr
import datetime

if __name__ == '__main__':

    ###Set paths and specify ICA/template data
    #########################################################
    basedir = '/home/jagust/jelman/rsfmri_ica/data'

    ### output directory
    outdir = os.path.join(basedir, 'OldICA_IC30_ecat_6mm_125.gica', 'dual_regress')
    if os.path.isdir(outdir)==False:
        os.mkdir(outdir)      
    else:
        #If outdir exists, rename existing outdirdir with timestamp appended
        mtime = os.path.getmtime(outdir)
        tmestamp = datetime.datetime.fromtimestamp(mtime).strftime('%Y-%m-%d_%H-%M-%S')
        newdir = '_'.join([outdir,tmestamp])
        os.rename(outdir,newdir)
        os.mkdir(outdir)
        print outdir, 'exists, moving to ', newdir

    ### Specify input data filelist, otherwise searches basedir for data
    if len(sys.argv) ==2:   #If specified, load file as list of infiles
        args = sys.argv[1]
        print 'Using data specified in ', args
        with open(args, 'r') as f:
            infiles = f.read().splitlines()
    else:    #If no infile given, search for data
        print 'No inputs specified, searching for data in ', basedir
        # look for subjects already registered filtered func ica data
        globstr = os.path.join(basedir, #data directory
                                'B*', #subject directory
                                'func', #functional data directory
                                'B*.ica', # subject speccific
                                'reg_standard', # registered to standard
                                'filtered_func_data.nii.gz') # data
        infiles = glob(globstr)
        infiles.sort()
        
    ### location for 4D template components (eg melodic_ICA, laird_4D)
    template = os.path.join(basedir, 'OldICA_IC30_ecat_6mm_125.gica',
                             'groupmelodic.ica','melodic_IC.nii.gz')

    num_ics = 30 #Number of ICs in 4d file. Components 0 thru <num_ics> will be merged.



    ### get mask from groupica
    mask = os.path.join(basedir,
                        'OldICA_IC30_ecat_6mm_125.gica',
                        'mask.nii.gz')



    ### RUN DUAL REGRESSION
    ############################
    startdir = os.getcwd()
    os.chdir(outdir)
    
    subd = {}
    for tmpf in infiles: #subject-wise
        subid = pydr.get_subid(tmpf)
        ###Run dr_stage1
        txtf = pydr.template_timeseries_sub(tmpf, template, mask, outdir)

        ###Run dr_stage2
        ## If you want to add movement params & spike regressors to stage2 of model
        ## mvtfile = [confound file] 
        ## Must change input of mvt parameter from None in dr_stage2 below
        mvtfile = os.path.join(basedir,
                            subid,
                            'func/data_QA',
                            'prefiltered_func_data_mcf.par') #Name of confound file

        stage2_ts, stage2_tsz = pydr.sub_spatial_map(tmpf, txtf, mask, outdir,
                                     desnorm=1, mvt=mvtfile)
        
        subd.update({subid:stage2_ts})

        ###Split subject 4d file into separate 3d files for each component
        allic = pydr.split_components(stage2_ts, subid, outdir)


    ###Concat ics across subjects.
    ###Only merges ICs from gica, 
    ###not those of confound regressors
    ###############################################
    for cn, item in enumerate(allic[:num_ics]): #Search through ics using last subject's output
        datadir, ic = os.path.split(item)       
        subid = pydr.get_subid(item)
        globstr = ic.replace(subid, '*')
        mergefile, subject_order = pydr.merge_components(datadir,
                                                      globstr = globstr)
        outfile = os.path.join(outdir, 'subject_order_ic%04d'%cn)
        with open(outfile, 'w+') as fid: 
            fid.write('\n'.join(subject_order)) #Write out subject order for each ic

    os.chdir(startdir)
        
