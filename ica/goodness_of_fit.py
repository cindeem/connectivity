"""
So the correlation maps for the atrophied ROIs in the large control cohort are saved in:
/home/jagust/manja/UCSF/Manja_Lehmann/ICN/data/large_control_sample/analysis/Migliaccio_ROIs/8mm_ROIs
We can probably ignore the precuneus seed for now. So the networks of interest would be:

8mm_alternative_PCA_seed_mid_occ_35.0_-84.0_6.0/

8mm_EOAD_seed_mid_frontal_40.0_42.0_30.0/

8mm_LPA_seed_sup_temp_sulcus_-56.0_-40.0_1.0/

use the controls_large_cohort_age_gender_tstat1.nii.gz

The actual seeds are saved in:

/home/jagust/manja/UCSF/Manja_Lehmann/ICN/data/seeds_of_interest/Migliaccio_seeds

"""
import os
from glob import glob
import numpy as np
import nibabel as ni
from scipy.ndimage import affine_transform

def reslice_data(img, change_dat, change_aff):
    """ reslices data in space_define_file to matrix of
    resample_file
    Parameters
    ----------
    space_define_file :  filename of space defining image
    resample_file : filename of image be resampled

    Returns
    -------
    img : space_define_file as nibabel image
    data : ndarray of data in resample_file sliced to
           shape of space_define_file
    """

    T = np.eye(4)
    
    Tv = np.dot(np.linalg.inv(change_aff), 
                np.dot(T, img.get_affine()))
    data = affine_transform(change_dat.squeeze(), 
                            Tv[0:3,0:3], 
                            offset=Tv[0:3,3], 
                            output_shape = img.get_shape()[:3],
                            order=0,mode = 'nearest')

    return  data


def get_connectome_networks(metaica, thresh=3):
    """
    connectome metaICA.nii.gz (4d) (input metaica file)
    splits into components and theshold at thresh
    (default thresh is 3 per visualization from paper)
    input dim is (61,73,61), resolution (3,3,3)
    return binarized thresholded 4d nipy image
    """
    img = ni.load(metaica)
    dat  = img.get_data()
    dat[dat < thresh] = 0
    #dat[dat >=3 ] = 1
    newimg = ni.Nifti1Image(dat, img.get_affine(), ni.Nifti1Header())
    return newimg

def get_grecious_networks(indir):
    """given indir get the nii.gz files in each network
    directory,
    return dict of {networkname: networkfile}
    input dim is (91,1009,91), resolution (2,2,2)
    """
    globstr = os.path.join(indir, '*', '*.nii.gz')
    allnet = glob(globstr)
    allnet.sort()
    if len(allnet) < 1:
        raise IOError('found no images in %s'%globstr)
    outd = {}
    for item in allnet:
        pth, _ = os.path.split(item)
        _, name = os.path.split(pth)
        outd[name] = item
    return outd
        
def get_graymask(infile, threshold=.2):
    """ opens graymask
    thresholds at threshold (default .2), binarizes
    return nibabel image
    """
    img = ni.load(infile)
    dat = img.get_data()
    dat[dat < threshold] = 0
    dat[dat>=threshold] = 1
    newimg = ni.Nifti1Image(dat, img.get_affine(),  ni.Nifti1Header())
    return newimg


def calc_gof(input, template, mask):
    """
    mask mask with template to get network, non-network
    get mean of input in mask and mean of network not in mask
    calc gof = abs(networkmean - nonnetwork_mean)
    return gof
    """
    network = np.logical_and(template > 0, mask>0)
    non_network = np.logical_and(template == 0 , mask > 0)
    netz = input[network]
    nonnetz =  input[non_network]
    gof = netz.mean() - nonnetz.mean()
    return gof

def calc_grecious_connectome_gof(connectome_img, grecious_dict):
    """
    connectome_img : 4d nibabel image
    grecious_dict : dict of files for each network {name:file}
    mask = mask defined on template
    for each connectome network, calc GOF with Grecios defined networks
    """
    grecios_nets = sorted(grecious_dict.keys())

    dat = connectome_img.get_data()
    x,y,z,vols = dat.shape
    gofd = {}
    for i in range(vols):
        slice = dat[:,:,:,i]
        tmpgof = []
        
        for cmptn, (name, file) in enumerate(sorted(grecious_dict.items())):
            netimg = ni.load(file)
            netdat = netimg.get_data()
            network =  netdat > 0
            non_network = np.logical_and(netdat <= 0 ,
                                         slice >0)
            netz = slice[network]
            nonnetz =  slice[non_network]
            gof = netz.mean() #- nonnetz.mean()
            tmpgof.append([cmptn,gof])
        
        tmpgof = np.array(tmpgof)
        tmpgof = tmpgof[tmpgof[:,1].argsort(),]
        print tmpgof, '\n'
        gofd[i] = [[grecios_nets[int(tmpgof[-1,0])],tmpgof[-1,1]],
                   [grecios_nets[int(tmpgof[-2,0])],tmpgof[-2,1]]]
    
    return gofd       
    

if __name__ == '__main__':

    #mask = '/home/jagust/cindeem/CODE/manja/Template_6_91_109_91.nii.gz'
    #mask = '/home/jagust/UCSF/Manja_Lehmann/ICN/rsfMRI_in_CONTROLS/data/NIC_3T_controls/template/r91_109_91_dartel_Mar_19_2012_07_04_6.nii'
    mask = '/home/jagust/UCSF/Manja_Lehmann/ICN/rsfMRI_in_CONTROLS/data/NIC_3T_controls/template/r91_109_91_dartel_Jun_30_2012_17_30_6.nii'
    #mask = '/home/jagust/UCSF/Manja_Lehmann/ICN/rsfMRI_in_AD/data/prelim_cohort_10control_30AD/template/r91_109_91_dartel_Dec_23_2011_01_47_6.nii'

    #metaica = '/home/jagust/cindeem/CODE/manja/templates-connectome/metaICA_91_109_91.nii.gz'
    metaica = '/home/jagust/manja/UCSF/Manja_Lehmann/ICN/rsfMRI_in_CONTROLS/data/network_templates/metaICA_91_109_91.nii.gz'
    #metaica = '/home/jagust/manja/UCSF/Manja_Lehmann/ICN/rsfMRI_in_AD/data/network_templates/metaICA_91_109_91.nii.gz'
    
    #grec_dir = '/home/jagust/cindeem/CODE/manja/templates-Greicius-cerebctx2012'
    #grec_dir = '/home/jagust/UCSF/Manja_Lehmann/ICN/rsfMRI_in_CONTROLS/data/templates-Greicius-cerebctx2012'
    #grec_dir = '/home/jagust/UCSF/Manja_Lehmann/ICN/rsfMRI_in_CONTROLS/data/Greicius_templates_of_interest'
    #grec_dir = '/home/jagust/UCSF/Manja_Lehmann/ICN/rsfMRI_in_CONTROLS/data/network_templates/Greicius_templates_of_interest'
    #grec_dir = '/home/jagust/UCSF/Manja_Lehmann/ICN/rsfMRI_in_CONTROLS/data/network_templates/templates-Greicius-cerebctx2012'
    #grec_dir = '/home/jagust/UCSF/Manja_Lehmann/ICN/rsfMRI_in_AD/data/network_templates/templates-Greicius-cerebctx2012'
    #grec_dir = '/home/jagust/manja/UCSF/Manja_Lehmann/ICN/rsfMRI_in_CONTROLS/data/network_templates/testing'
    grec_dir = '/home/jagust/manja/UCSF/Manja_Lehmann/ICN/rsfMRI_in_CONTROLS/data/network_templates/Greicius_and_DMN_components'

    #netdir = '/home/jagust/UCSF/Manja_Lehmann/ICN/data/large_control_sample/analysis/Migliaccio_ROIs/8mm_ROIs'
    #netdir = '/home/jagust/UCSF/Manja_Lehmann/ICN/rsfMRI_in_CONTROLS/analysis/NIC_3T_controls/Migliaccio_ROIs/4mm_ROIs/112controls_old_cohort_delete'
    #netdir = '/home/jagust/UCSF/Manja_Lehmann/ICN/rsfMRI_in_CONTROLS/analysis/NIC_3T_controls/Migliaccio_ROIs/4mm_ROIs'
    #netdir = '/home/jagust/manja/UCSF/Manja_Lehmann/ICN/rsfMRI_in_CONTROLS/analysis/NIC_3T_controls/dorsal_DMN_seeds'
    #netdir = '/home/jagust/manja/UCSF/Manja_Lehmann/ICN/rsfMRI_in_AD/analysis/preliminary_cohort_controls_AD_40sbj/voxel-wise_seed_based_correlations/randomise/Migliaccio_ROIs/4mm_ROIs'
    #netdir = '/home/jagust/manja/UCSF/Manja_Lehmann/ICN/rsfMRI_in_AD/analysis/preliminary_cohort_controls_AD_40sbj/voxel-wise_seed_based_correlations/randomise/Migliaccio_ROIs/8mm_ROIs'
    #netdir = '/home/jagust/UCSF/Manja_Lehmann/ICN/rsfMRI_in_CONTROLS/analysis/NIC_3T_controls/FDG_seeds'
    #netdir = '/home/jagust/UCSF/Manja_Lehmann/ICN/rsfMRI_in_CONTROLS/analysis/NIC_3T_controls/Migliaccio_ROIs/4mm_ROIs/Specifically_atrophied_ROIs'
    #netdir = '/home/jagust/UCSF/Manja_Lehmann/ICN/rsfMRI_in_CONTROLS/analysis/NIC_3T_controls/Migliaccio_ROIs/4mm_ROIs/Commonly_atrophied_ROIs'
    #netdir = '/home/jagust/UCSF/Manja_Lehmann/ICN/rsfMRI_in_CONTROLS/analysis/NIC_3T_controls/Migliaccio_ROIs/4mm_ROIs/Max_atrophied_comp_controls_ROIs'
    #netdir = '/home/jagust/manja/UCSF/Manja_Lehmann/ICN/rsfMRI_in_AD/analysis/preliminary_cohort_controls_AD_40sbj/voxel-wise_seed_based_correlations/randomise/Stanford_DMN_components'
    #netdir = '/home/jagust/manja/UCSF/Manja_Lehmann/ICN/rsfMRI_in_CONTROLS/analysis/NIC_3T_controls/Migliaccio_ROIs/4mm_ROIs/overlap/masking'
    #netdir = '/home/jagust/manja/UCSF/Manja_Lehmann/ICN/rsfMRI_in_CONTROLS/analysis/NIC_3T_controls/Migliaccio_ROIs/4mm_ROIs/Commonly_atrophied_ROIs/new'
    #netdir = '/home/jagust/manja/UCSF/Manja_Lehmann/ICN/rsfMRI_in_CONTROLS/analysis/NIC_3T_controls/Migliaccio_ROIs/rerun_SPM8'
    #netdir = '/home/jagust/manja/UCSF/Manja_Lehmann/ICN/rsfMRI_in_CONTROLS/analysis/NIC_3T_controls/Migliaccio_ROIs/from_paper_SPM2/Specifically_atrophied_ROIs'
    netdir = '/home/jagust/manja/UCSF/Manja_Lehmann/ICN/rsfMRI_in_CONTROLS/analysis/NIC_3T_controls/Migliaccio_ROIs/from_paper_SPM2'
        
    # subject networks
    #networks = ['8mm_alternative_PCA_seed_mid_occ_35.0_-84.0_6.0',
                #'8mm_EOAD_seed_mid_frontal_40.0_42.0_30.0',
                #'8mm_LPA_seed_sup_temp_sulcus_-56.0_-40.0_1.0']
    #networks = ['8mm_All_seed_PCC_-2.0_-33.0_28.0',
    		#'8mm_All_seed_precuneus_-2.0_-60.0_44.0']	
		
    #networks = ['8mm_EOAD_seed_mid_frontal_40.0_42.0_30.0']

    #networks = ['4mm_EOAD_seed_mid_frontal_40.0_42.0_30.0']
    #networks = ['4mm_LPA_seed_sup_temp_sulcus_-56.0_-40.0_1.0']
    #networks = ['4mm_PCA_seed_mid_occ_39.0_-88.0_10.0']
    #networks = ['4mm_EOAD_seed_mid_frontal_40.0_42.0_30.0/separate_hemispheres']
    #networks = ['4mm_All_seed_PCC_-2.0_-33.0_28.0']
    #networks = ['4mm_All_seed_precuneus_-2.0_-60.0_44.0']
    #networks = ['4mm_All_seed_infpariet_-51.0_-58.0_37.0']
    #networks = ['overlap/binarized_maps']
    #networks = ['4mm_EOAD_seed_inf_parietal_60.0_-54.0_36.0']
    #networks = ['4mm_LPA_seed_inf_parietal_-51.0_-58.0_37.0']
    #networks = ['4mm_PCA_seed_MTG_50.0_-64.0_19.0']
    #networks = ['overlap/binarized_maps/max_atrophied_maps']
    #networks = ['4mm_All_seed_infpariet2_-53.0_-54.0_29.0']
    #networks = ['4mm_All_seed_MTG_-46.0_-68.0_18.0']
    #networks = ['4mm_All_seed_infpariet3_62.0_-49.0_39.0']
    #networks = ['4mm_All_seed_left_mid_occ_-32.0_-83.0_30.0']
    #networks = ['4mm_All_seed_right_mid_occ_52.0_-74.0_6.0']
    #networks = ['4mm_All_seed_sup_temp_-54.0_-37.0_15.0']
    #networks = ['4mm_LPA_seed_MTG_-46.0_-68.0_18.0']
    

    #networks = ['4mm_EOAD_seed_inf_parietal_60.0_-54.0_36.0/removing_cerebellum']
    #networks = ['4mm_LPA_seed_inf_parietal_-51.0_-58.0_37.0/removing_cerebellum']

    #networks = ['4mm_inferior_parietal_60.0_-48.0_36.0']

    #networks = ['4mm_EOAD_seed_mid_frontal_40.0_42.0_30.0/controls/MNI_mask']
    #networks = ['4mm_EOAD_seed_mid_frontal_40.0_42.0_30.0/ad/MNI_mask']
    #networks = ['4mm_EOAD_seed_mid_frontal_40.0_42.0_30.0/lpa/MNI_mask']
    #networks = ['4mm_EOAD_seed_mid_frontal_40.0_42.0_30.0/pca/MNI_mask']
    #networks = ['4mm_LPA_seed_sup_temp_sulcus_-56.0_-40.0_1.0/controls/MNI_mask']
    #networks = ['4mm_LPA_seed_sup_temp_sulcus_-56.0_-40.0_1.0/ad/MNI_mask']
    #networks = ['4mm_LPA_seed_sup_temp_sulcus_-56.0_-40.0_1.0/lpa/MNI_mask']
    #networks = ['4mm_LPA_seed_sup_temp_sulcus_-56.0_-40.0_1.0/pca/MNI_mask']
    #networks = ['4mm_PCA_seed_mid_occ_39.0_-88.0_10.0/controls/MNI_mask']
    #networks = ['4mm_PCA_seed_mid_occ_39.0_-88.0_10.0/ad/MNI_mask']
    #networks = ['4mm_PCA_seed_mid_occ_39.0_-88.0_10.0/lpa/MNI_mask']
    #networks = ['4mm_PCA_seed_mid_occ_39.0_-88.0_10.0/pca/MNI_mask']
    #networks = ['4mm_All_seed_precuneus_-2.0_-60.0_44.0/controls/MNI_mask']
    #networks = ['4mm_All_seed_precuneus_-2.0_-60.0_44.0/ad/MNI_mask']
    #networks = ['4mm_All_seed_precuneus_-2.0_-60.0_44.0/lpa/MNI_mask']
    #networks = ['4mm_All_seed_precuneus_-2.0_-60.0_44.0/pca/MNI_mask']

    #networks = ['8mm_EOAD_seed_mid_frontal_40.0_42.0_30.0/controls/MNI_mask']

    #networks = ['4mm_EOAD_FDG_seed_-48.0_-54.0_18.0']
    #networks = ['4mm_LPA_FDG_seed_-48.0_-52.0_14.0']
    #networks = ['4mm_PCA_FDG_seed_-42.0_-68.0_-2.0']

    #networks = ['8mm_dDMN_seed_-4.0_52.0_0.0/controls']
    #networks = ['8mm_High-visual_seed_36.0_-88.0_0.0/controls']
    #networks = ['8mm_Language_seed_-54.0_-56.0_22.0/controls']
    #networks = ['8mm_LECN_seed_-38.0_-68.0_48.0/controls']
    #networks = ['8mm_RECN_seed_52.0_-46.0_48.0/controls']
    #networks = ['8mm_vDMN_seed_-4.0_-58.0_56.0/controls']

    #networks = ['8mm_dDMN_seed_-4.0_52.0_0.0/EOAD']
    #networks = ['8mm_High-visual_seed_36.0_-88.0_0.0/EOAD']
    #networks = ['8mm_Language_seed_-54.0_-56.0_22.0/EOAD']
    #networks = ['8mm_LECN_seed_-38.0_-68.0_48.0/EOAD']
    #networks = ['8mm_RECN_seed_52.0_-46.0_48.0/EOAD']
    #networks = ['8mm_vDMN_seed_-4.0_-58.0_56.0/EOAD']

    #networks = ['8mm_dDMN_seed_-4.0_52.0_0.0/LPA']
    #networks = ['8mm_High-visual_seed_36.0_-88.0_0.0/LPA']
    #networks = ['8mm_Language_seed_-54.0_-56.0_22.0/LPA']
    #networks = ['8mm_LECN_seed_-38.0_-68.0_48.0/LPA']
    #networks = ['8mm_RECN_seed_52.0_-46.0_48.0/LPA']
    #networks = ['8mm_vDMN_seed_-4.0_-58.0_56.0/LPA']

    #networks = ['8mm_dDMN_seed_-4.0_52.0_0.0/PCA']
    #networks = ['8mm_High-visual_seed_36.0_-88.0_0.0/PCA']
    #networks = ['8mm_Language_seed_-54.0_-56.0_22.0/PCA']
    #networks = ['8mm_LECN_seed_-38.0_-68.0_48.0/PCA']
    #networks = ['8mm_RECN_seed_52.0_-46.0_48.0/PCA']
    #networks = ['8mm_vDMN_seed_-4.0_-58.0_56.0/PCA']

    #networks = ['8mm_aDMN_seed_-2.0_50.0_-4.0/controls']
    #networks = ['8mm_pDMN_seed_2.0_-68.0_36.0/controls']
    #networks = ['8mm_vDMN_seed_42.0_-76.0_28.0/controls']

    #networks = ['8mm_aDMN_seed_-2.0_50.0_-4.0/EOAD']
    #networks = ['8mm_pDMN_seed_2.0_-68.0_36.0/EOAD']
    #networks = ['8mm_vDMN_seed_42.0_-76.0_28.0/EOAD']

    #networks = ['8mm_aDMN_seed_-2.0_50.0_-4.0/LPA']
    #networks = ['8mm_pDMN_seed_2.0_-68.0_36.0/LPA']
    #networks = ['8mm_vDMN_seed_42.0_-76.0_28.0/LPA']
    
    #networks = ['8mm_aDMN_seed_-2.0_50.0_-4.0/PCA']
    #networks = ['8mm_pDMN_seed_2.0_-68.0_36.0/PCA']
    #networks = ['8mm_vDMN_seed_42.0_-76.0_28.0/PCA']

    #networks = ['common_ROIs']
    #networks = ['max_ROIs']
    #networks = ['4mm_All_seed_precentral_-42.0_3.0_38.0']
    #networks = ['4mm_All_seed_inf_frontal_-44.0_16.0_30.0']

    #networks = ['common_ROIs/4mm_left_parahpc_-29.0_2.0_-23.0']
    #networks = ['common_ROIs/4mm_left_postcing_-8.0_-51.0_33.0']
    #networks = ['common_ROIs/4mm_right_parahpc_30.0_3.0_-24.0']
    #networks = ['max_ROIs/4mm_EOAD_seed_left_precuneus_-9.0_-51.0_36.0']
    #networks = ['max_ROIs/4mm_LPA_seed_left_suptemp_-63.0_-48.0_22.0']
    #networks = ['max_ROIs/4mm_PCA_seed_right_midcing_3.0_-34.0_34.0']
    #networks = ['specific_ROIs/4mm_EOAD_seed_right_precuneus_3.0_-51.0_48.0']
    #networks = ['specific_ROIs/4mm_LPA_seed_left_midtemp_-62.0_-19.0_-8.0']
    #networks = ['specific_ROIs/4mm_PCA_seed_right_supocc_30.0_-70.0_43.0']

    networks = ['seed_masked_correlation_maps']

    
    connectome = get_connectome_networks(metaica, thresh=3)
    grec = get_grecious_networks(grec_dir)
    #gmmaskf = '/home/jagust/cindeem/CODE/manja/Template_6_91_109_91.nii.gz'
    #gmmaskf = '/home/jagust/UCSF/Manja_Lehmann/ICN/rsfMRI_in_CONTROLS/data/NIC_3T_controls/template/r91_109_91_dartel_Mar_19_2012_07_04_6.nii'
    gmmaskf = '/home/jagust/UCSF/Manja_Lehmann/ICN/rsfMRI_in_CONTROLS/data/NIC_3T_controls/template/r91_109_91_dartel_Jun_30_2012_17_30_6.nii'
    #gmmaskf = '/home/jagust/UCSF/Manja_Lehmann/ICN/rsfMRI_in_AD/data/prelim_cohort_10control_30AD/template/r91_109_91_dartel_Dec_23_2011_01_47_6.nii'
    
    maskimg = get_graymask(gmmaskf, threshold=.2)
    maskdat = maskimg.get_data()
    gof = calc_grecious_connectome_gof(connectome, grec)
    networks = [os.path.join(netdir,
                             x,
                             'PCA_seed_masked_PCA_corr_map.nii.gz') for x in networks] ##use normal tstat file here, not fwe corrected file
    x,y,z,nvols = connectome.get_shape()
    connectome_dat = connectome.get_data()
    gof = {}
    for network in networks:
        
        netdat = ni.load(network).get_data()
        tmpgof = []
        for name, f in grec.items():
        #for i in range(nvols):
            #template = connectome_dat[:,:,:,i]
            template = ni.load(f).get_data()
            tgof = calc_gof(netdat, template, maskdat)
            #tmpgof.append([i,tgof])
            tmpgof.append([name,tgof])
        tmpgof = np.array(tmpgof)
        tmpgof = tmpgof[tmpgof[:,1].astype(float).argsort(),]
        gof[network] = tmpgof[-2]   # tmpgof[-2] is second best fit network
        
    """
    fid = open('gof_networks.csv', 'w+')
    for network in gof:
        fid.write('%s,%2.2f,%2.2f,\n'%(network, gof[network]))
    fid.close()
        
    """
