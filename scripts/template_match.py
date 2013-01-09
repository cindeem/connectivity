import sys
import nibabel as nib
sys.path.insert(0, '/home/jagust/cindeem/CODE/connectivity/match')


def LoadData(infile):
    img = nib.load(infile)
    dat = img.get_data()
    return dat


###########################
#Set filenames
###########################################
#ICA components file to match to template
icafile = '/home/jagust/jelman/rsfmri_ica/data/Test/melodic_IC.nii.gz'
#Template to match components to, can be 4D file.
tempfile = '/home/jagust/jelman/rsfmri_ica/data/Test/Laird2011_4d_3mm.nii.gz'
#Mask to restrict voxels which are matched
maskfile = '/usr/local/fsl-5.0.1/data/standard/MNI152_T1_1mm_brain_mask.nii.gz'
#File mapping 4D template volume number to description
mapfile = '/home/jagust/jelman/rsfmri_ica/data/Test/template_mapping.txt'
###########################################

#Load component file, template and mask
icadat = LoadData(icafile)
tempdat = LoadData(tempfile)
maskdat = LoadData(maskfile)

#Load text file of template network names to dict.
template_map = {}
with open(mapfile) as f:
    for line in f:
       (key, val) = line.split()
       template_map[int(key)] = val




