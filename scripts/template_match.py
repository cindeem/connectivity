import sys
import nibabel as nib
sys.path.insert(0, '/home/jagust/jelman/rsfmri_ica/code/connectivity/match')
import matching
import pandas
import os

"""
Wrapper script to generate template matching metrics between ICA components and
a given set of network templates. 

Edit inputs
----------
datapath : str
    path to project directory
icafile : str
    4D image file of ICA componenets (e.g. melodic_IC.nii.gz)
tempfile : str
    4D image file of network templates to match 
mapfile : str
    text file mapping network names to volumes in tempfile
maskfile : str
    3D image file to restrict which voxels are included in matching
outdir : str
    path to output results
outfile : str
    name of csv output listing metrics

Output
----------
CSV file listing matching metrics between each component and every network template.

"""


def LoadTemplate(mapfile):
    """
    Loads text file of template volume mapping to dict.
    mapfile: First column=volume number (begin with 1), 2nd column=network name
    """
    template_map = {}
    with open(mapfile) as f:
        for line in f:
           (key, val) = line.split()
           template_map[int(key)] = val
    return template_map

if __name__ == '__main__':


    #Set filenames and paths
    ##############################################
    datapath='/home/jagust/jelman/rsfmri_ica/data/'
    #Group ICA output
    icafile = os.path.join(datapath,
                            'OldICA_IC0_ecat_2mm_6fwhm_125.gica/groupmelodic.ica',
                            'melodic_IC.nii.gz') 
    #Template to match components to. 4D file.
    tempfile = os.path.join('/home/jagust/jelman/templates',
                            'templates-Greicius-cerebctx2012',
                            'Grecius_2012_4d_2mm.nii.gz') 
    #File mapping 4D template volume number to description
    mapfile = os.path.join('/home/jagust/jelman/templates',
                            'templates-Greicius-cerebctx2012',
                            'template_mapping.txt')
    #Mask to restrict voxels which are matched (MNI example below)
    #maskfile = os.path.join(os.environ['FSLDIR'],
    #                        'data/standard', 
    #                        'MNI152_T1_2mm_brain_mask.nii.gz')
    maskfile = os.path.join('/home/jagust/jelman/templates',
                            'MNI152_T1_2mm_brain_mask.nii.gz')


    #Set output directory of matching metrics
    outdir = os.path.join(datapath,
                            'OldICA_IC0_ecat_2mm_6fwhm_125.gica')
    outfile = 'MatchingMetrics_Greicius2012.csv'
    #Descriptive list of metrics to be run.
    #Used when generating columns of output
    metrics = ['gof', 'eta', 'pear_r', 'pear_p']


    #Load 4d ICA output, 4d template images and mask image
    ########################################################
    icaimg = nib.load(icafile)      #4D group ICA output
    icadat = icaimg.get_data()
    tempimg = nib.load(tempfile)    #4D template for matching
    tempdat = tempimg.get_data()
    maskimg = nib.load(maskfile)    #Mask to restrict gof calculation
    maskdat = maskimg.get_data()

    #Get shape of ICA data. 't' represents number of components
    x, y, z, t = icadat.shape


    #Load text file of template network names to dict.
    ##########################################################
    template_map = {}
    with open(mapfile) as f:
        for line in f:
           (key, val) = line.split()
           template_map[int(key)] = val    


    ##Create frame to hold output.
    #Rows: network names
    #Columns: Level1=ICA component number (0-based). Level2=Metric scores.
    #########################################################################
    level_tuples = []
    for i in range(t):
        for j in metrics:
            level_tuples.append((str(i),j))
    row_index = pandas.MultiIndex.from_tuples(level_tuples, 
                                names=['Component', 'Metric']) #Level1 and Level2 names

    #Create empty dataframe to hold metric scores
    matchframe = pandas.DataFrame(index=row_index, columns=template_map.values())

    #Calculate matching metrics of all components with template networks  
    for cmpnt in range(t):  #Loop over all components in 4d ICA file
        icavol = icadat[:,:,:,cmpnt]

        for net in template_map.keys(): #Loop over all networks in 4d template
            tempvol = tempdat[:,:,:,(net - 1)]
            tempname = template_map[net]
            gof = matching.calc_gof(icavol, #Calc goodness of fit (Greicius 2004)
                                    tempvol,
                                    maskdat)
            (eta, (pear_r, pear_p)) = matching.calc_eta(icavol, #Calc Cohen's eta
                                                    tempvol, 
                                                    getr=True)
            matchframe.ix[str(cmpnt),'gof'][tempname] = gof
            matchframe.ix[str(cmpnt),'eta'][tempname] = eta
            matchframe.ix[str(cmpnt),'pear_r'][tempname] = pear_r
            matchframe.ix[str(cmpnt),'pear_p'][tempname] = pear_p

    saveout = os.path.join(outdir, outfile)
    matchframe.to_csv(saveout, header=True, index=True)   #Save to file

