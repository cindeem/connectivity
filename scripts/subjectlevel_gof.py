import os, sys
import nibabel as ni
import numpy as np
from glob import glob
import pandas
import argparse
sys.path.insert(0, '/home/jagust/jelman/rsfmri_ica/code/connectivity/match')
import matching


def get_subjects_files(subdir):
    globstr = os.path.join(subdir, '*nii*')
    result = sorted(glob(globstr))
    if len(result) < 1:
        raise IOError('no files found %s'%(globstr))
    return result

def main(template, subjectsdir, thresh = 0, run_eta = False):
    tdat = ni.load(template).get_data().squeeze()

    _, tname = os.path.split(template)
    tname = tname.split('.')[0]
    subfiles = get_subjects_files(subjectsdir)
    allresults = []
    for sf in subfiles:
        pth, nme = os.path.split(sf)
        nme = nme.split('.')[0]
        tmpdat = ni.load(sf).get_data().squeeze()
        if not tmpdat.shape == tdat.shape:
            raise IndexError('shape mismatch: '+\
                             'template:%s, data: %s'%(tdat.shape, 
                                                      tmpdat.shape))
        mask = tmpdat > 0
        maskd_template = tdat.copy()
        maskd_template[tdat <=thresh] = 0
        maskd_template[tdat > thresh] = 1
        gof = matching.calc_gof(tmpdat, maskd_template, mask)
        res = [nme, gof]
        print res
        if run_eta:
            eta = matching.calc_eta(tmpdat[mask], tdat[mask])
            res.append(eta)
        allresults.append(res)
    columns = ['name', 'gof']
    if run_eta:
        columns.append('eta')
    df = pandas.DataFrame(allresults, columns = columns)
    outf = os.path.join(subjectsdir, 'matching_%s_data.xls'%(tname))
    df.to_excel(outf)
    print 'wrote %s'%(outf)


if __name__ == '__main__':

    """
    get template

    get subjects_zscore networks directory

    calc masked gof for each subject

    save to spreadsheet

    """
    parser = argparse.ArgumentParser(
            description = 'Use Template and subjects zscored networks to '+\
            'calulate a goodness of fit (GOF) with template for each subject')

    parser.add_argument('template', type=str, nargs=1,
                        help = 'Template to compare against (should be binary)')

    parser.add_argument('subsdir',type=str, nargs = 1, 
                        help = 'Directory containing subjects networks')

    parser.add_argument('-thr', type=float, default = 0,
                        help = 'Threshold for Template(default 0)')
    parser.add_argument('-eta', action = 'store_true', 
                        help = 'Calc ETA along with GOF, '+\
                               '(only with non-binary template)')
    if len(sys.argv) == 1:
        parser.print_help()
    else:
        args = parser.parse_args()

        print args.template[0], args.subsdir[0]
        print 'calc eta:', args.eta
        main(args.template[0], args.subsdir[0], args.thr, args.eta)
