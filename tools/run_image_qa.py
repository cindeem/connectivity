import sys, os
sys.path.append("/home/jagust/cindeem/CODE/PetProcessing/misc")
import rapid_art
import numpy as np

def CreateRegressors(outdir, art_output, num_vols):
    qa_file = os.path.join(outdir,'data_QA',art_output)
    outliers = np.loadtxt(qa_file, dtype=int)
    outliers = np.atleast_1d(outliers)
    outlier_array = np.zeros(num_vols,dtype=float)
    for i in range(len(outliers)):
        outlier_array[outliers[i]]=1
    outfile = os.path.join(outdir, 'data_QA', 'outliers_for_fsl.txt')
    outlier_array.tofile(outfile)
    np.savetxt(outfile, outlier_array, fmt='%i', delimiter=u'\t')
    print 'Saved %s'%outfile
    return outlier_array



def CombineRegressors(mc_params, outlier_array, confound_outname):
    if outlier_array.ndim > 1:
        combined = np.hstack((mc_params, outlier_array))
        outfile = os.path.join(funcdir, confound_outname)
        np.savetxt(outfile, combined, delimiter=u'\t')
    elif outlier_array.ndim == 1:
        combined = np.hstack((mc_params, np.atleast_2d(outlier_array).T))
        outfile = os.path.join(funcdir, confound_outname)
        np.savetxt(outfile, combined, delimiter=u'\t')
    print 'Saved %s'%outfile
    return combined



if __name__ == '__main__':

    if len(sys.argv) ==1:
        print 'USAGE: python run_image_qa.py Bxx-xxx Bxx-xxx Bxx-xxx'
    else:
        args = sys.argv[1:]

    #Set up paths for current study
    ####################################################
    datapath = '/home/jagust/jelman/rsfmri_ica/data'
    art_output = 'art.filtered_func_data.nii_outliers.txt'
    ####################################################

    for subj in args:
        subjdir = os.path.join(datapath,subj)
        #Declare run-level paths and files
        ######################################################
        funcdir = os.path.join(subjdir,'func')
        icafolder = ''.join([subj,'_4d_Preproc.feat'])
        infiles = [os.path.join(funcdir,icafolder, 'filtered_func_data.nii.gz')]
        param_file = os.path.join(funcdir,icafolder,'mc', 'prefiltered_func_data_mcf.par')
        param_source = 'FSL'
        thresh = 3
        outdir = funcdir
        confound_outname = 'confound_regressors_8mm.txt'
        ######################################################
        #Run artdetect and create QA directory
        rapid_art.main(infiles, param_file, param_source, thresh, outdir)

        #Generate motion-intensity regressor for FSL and save in QA folder.
        #Combine motion-intensity regressors with motion correction parameters. 
        #Save combined confound regressors to run directory.
        mc_params = np.loadtxt(param_file)
        num_vols = len(mc_params)
        outlier_array = CreateRegressors(outdir, art_output, num_vols)
        confound_regressors = CombineRegressors(mc_params, outlier_array, confound_outname) 

