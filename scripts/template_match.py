import sys
import nibabel as nib
sys.path.insert(0, '/home/jagust/jelman/rsfmri_ica/code/connectivity/match')
import matching
import pandas


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


###########################################
#Set filenames
###########################################
datapath='/home/jagust/jelman/rsfmri_ica/data/Test'

#Group ICA output
icafile = os.path.join(datapath,
                        'melodic_IC.nii.gz' 
#Template to match components to. 4D file.
tempfile = os.path.join(datapath,
                        'Laird2011_4d_MNI_3mm.nii.gz' 
#Mask to restrict voxels which are matched
maskfile = os.path.join(datapath,
                        'MNI152_T1_3mm_brain_mask.nii.gz' 

#File mapping 4D template volume number to description
mapfile = os.path.join(datapath,
                        'template_mapping.txt'

#Descriptive list of metrics to be run.
#Used when generating columns of output
metrics = ['gof', 'eta', 'pear_r', 'pear_p']
###########################################

#Load 4d ICA output, 4d template images and mask image
icaimg = nib.load(icafile)
icadat = icaimg.get_data()
tempimg = nib.load(tempfile)
tempdat = tempimg.get_data()
maskimg = nib.load(maskfile)
maskdat = maskimg.get_data()

#Load text file of template network names to dict.
template_map = LoadTemplate(mapfile)


#Get shape of ICA data. 't' represents number of components
x, y, z, t = icadat.shape

###Create frame to hold output.
#Rows = network names
#Columns = Level1: ICA component number, Level2: Metric value
level_tuples = []
for i in range(t):
    for j in metrics:
        level_tuples.append((str(i),j))
column_index = pandas.MultiIndex.from_tuples(level_tuples, 
                            names=['Component', 'Metric']) #Name Level1 and Level2

#Create empty dataframe for output of matching
matchframe = pandas.DataFrame(index=template_map.values(), columns=column_index)


#Calculate matching metrics of all components with template networks  
for cmpnt in range(t): #Loop over all components in 4d ICA file
    icavol = icadat[:,:,:,cmpnt]

    for net in template_map.keys():  #Loop over all networks in 4d template
        tempvol = tempdat[:,:,:,(net - 1)]
        tempname = template_map[net]
        gof = matching.calc_gof(icavol,
                                tempvol,
                                maskdat)
        (eta, (pear_r, pear_p)) = matching.calc_eta(icavol, 
                                                tempvol, 
                                                getr=True)
        matchframe.ix[tempname][str(cmpnt),'gof'] = gof
        matchframe.ix[tempname][str(cmpnt),'eta'] = eta
        matchframe.ix[tempname][str(cmpnt),'pear_r'] = pear_r
        matchframe.ix[tempname][str(cmpnt),'pear_p'] = pear_p

matchframe.to_csv('MatchingMetrics.csv', header=True, index=True)

