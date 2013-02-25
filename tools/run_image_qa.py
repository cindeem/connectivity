import sys, os
sys.path.append("/home/jagust/cindeem/CODE/PetProcessing/misc")
import rapid_art
import numpy as np

"""
Wrapper script to run rapid_art.py and create confound file for use with FSL or SPM

Parameters to edit in main script:
----------------------------------
datapath : str
    project directory containing data
art_output : str
    name of rapid_art.py output listing outlier volume numbers
funcdir : str
    functional data directory within subject folder
icafolder : str
    ica directory within subject's func directory
infiles : str
    pre-processed 4D functional data file
param_file : str
    motion correction parameter file (e.g. prefiltered_func_data_mcf.par)
param_source : 'FSL' or 'SPM'
    software used to create mc parameter file (default is 'SPM')
thresh = int
    z-score threshold to determine outlier volumes
outdir = str
    directory to output confound regressor text file
confound_outname = str
    name of confound regressor text file

Outputs: 
------------------
File output: <outdir>/<confound_outname>
    text file containing confound regressors for use in FSL or SPM model

Notes
-------------------
If no motion or intensity outliers exist, will save out only motion 
parameters. This means number of confound regressors are potentially 
different across subjects, verify that this will not cause problems for 
further processing when using confound regressor file.

"""


def CreateRegressors(funcdir, art_output, num_vols):
    """ takes list of outlier volumes output by rapid_art.py
    converts to array of same length as functional volume for use
    in FSL or SPM model

    Parameters
    -----------
    outdir : str
        directory to save regressor text file in
    art_output : str
        path to directory of rapid_art.py output
    num_vols : int
        number of volumes in pre-processed functional file
    

    Returns
    ----------
    exists : bool
        indicates whether outliers exist or if only mc parameters should
        be used as confounds
    outlier_array : numpy array
        array with value 1 for each outlier vol to be regressed out

    """
    exists = False
    qa_file = os.path.join(funcdir,'data_QA',art_output)
    outliers = np.loadtxt(qa_file, dtype=int)
    outliers = np.atleast_1d(outliers)
    if len(outliers) >= 1:
        exists = True
        outlier_array = np.zeros(num_vols,dtype=float)
        for i in range(len(outliers)):
            outlier_array[outliers[i]]=1
        outfile = os.path.join(funcdir, 'data_QA', 'outliers_for_fsl.txt')
        outlier_array.tofile(outfile)
        np.savetxt(outfile, outlier_array, fmt='%i', delimiter=u'\t')
        print 'Saved %s'%outfile
        return exists, outlier_array
    elif len(outliers)==0:
        outlier_array = np.array([])
        print 'No outliers, only mc parameters will be used'
        return exists, outlier_array



def CombineRegressors(mc_params, outlier_array, outdir, confound_outname):
    """ combines array of motion parameters and spike regressor
    to be used as confound file in SPM or FSL model

    Parameters
    -----------
    mc_params : numpy array
        array containing motion correction parameters for each volume
    outlier_array : numpy array
        array of spike regressors corresponding to outlier volumes
    confound_outname : str
        name of file to save confound regressors to

    Returns
    -----------
    combined : numpy array
        array of confound regressors for use in model
        columns of confound regressors with one row per timepoint

    """
    if outlier_array.ndim > 1:
        combined = np.hstack((mc_params, outlier_array))
        outfile = os.path.join(outdir, confound_outname)
        np.savetxt(outfile, combined, delimiter=u'\t')
    elif outlier_array.ndim == 1:
        combined = np.hstack((mc_params, np.atleast_2d(outlier_array).T))
        outfile = os.path.join(outdir, confound_outname)
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
        icafolder = ''.join([subj,'_4d_OldICA_IC0_ecat_2mm_6fwhm_125.ica'])
        infiles = [os.path.join(funcdir,icafolder, 'filtered_func_data.nii.gz')]
        param_file = os.path.join(funcdir,icafolder,'mc', 'prefiltered_func_data_mcf.par')
        param_source = 'FSL'
        thresh = 3
        outdir = funcdir
        confound_outname = 'confound_regressors_6mm.txt'
        ######################################################
        #Run artdetect and create QA directory
        rapid_art.main(infiles, param_file, param_source, thresh, outdir)

        #Generate motion-intensity regressor for FSL and save in QA folder.
        #Combine motion-intensity regressors with motion correction parameters. 
        #Save combined confound regressors to run directory.
        mc_params = np.loadtxt(param_file)
        num_vols = len(mc_params)
        exists, outlier_array = CreateRegressors(funcdir, art_output, num_vols)
        if exists:
            confound_regressors = CombineRegressors(mc_params, 
                                                    outlier_array, 
                                                    outdir, confound_outname) 
        elif not exists:
            outfile = os.path.join(outdir, confound_outname)
            np.savetxt(outfile, mc_params, delimiter=u'\t')
            print 'Saved %s'%outfile

