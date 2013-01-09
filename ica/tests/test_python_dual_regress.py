# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:
import os, sys, re
from os.path import (abspath, join, dirname, exists)
from tempfile import mkdtemp
import nibabel as ni
from unittest import TestCase, skipIf, skipUnless
from numpy.testing import (assert_raises, assert_equal, assert_almost_equal)
from numpy import (loadtxt, array, concatenate)
from .. import python_dual_regress as pydr


def get_data_dir():
    """ return directory holding data for tests"""
    return join(os.path.dirname(__file__), 'data')

def tmp_outdir():
    """ returns a temporary directory to store tests outputs"""
    return mkdtemp()

def clean_tmpdir(tmpdir):
    os.system('rm -rf %s'%tmpdir)

def test_get_subid():
    # basic
    instr = '/bunch/of/jnk/B00-000'
    subid = pydr.get_subid(instr)
    assert_equal(subid, 'B00-000')
    # user specified pattern
    pattern = 'PIDN_[0-9]{5}_[0-9]{2}_[0-9]{2}_[0-9]{4}'
    instr = '/path/to/nowhere/PIDN_09120_09_18_2009/more/jnk'
    subid = pydr.get_subid(instr, pattern=pattern)
    assert_equal(subid, 'PIDN_09120_09_18_2009')
    # test multi
    sid = 'B09-220'
    instr = join('/some/junk', sid, 'more/junk', sid)
    subid = pydr.get_subid(instr)
    assert_equal(subid, sid)

def test_find_component_number():
    instr = '/path/to/dr_stage2_B09-230_ic0040.nii.gz'
    comp = pydr.find_component_number(instr)
    assert_equal(comp, 'ic0040')
    pattern = 'ic[0-9]{2}'
    comp = pydr.find_component_number(instr, pattern=pattern)
    assert_equal(comp, 'ic00')

def test_concat_regressors():
    datadir = get_data_dir()
    a = join(datadir, 'example_B00-000.txt')
    b = join(datadir, 'example_movement.txt')
    outdir = tmp_outdir()
    outf = pydr.concat_regressors(a, b, outdir = outdir)
    adat = loadtxt(a)
    bdat = loadtxt(b)
    cdat = loadtxt(outf)
    assert_almost_equal(concatenate((adat,bdat), axis=1),cdat)
    # test txt file reading
    mask = join(datadir, 'mask.nii.gz')
    assert_raises(IOError, pydr.concat_regressors,a,mask)
    # test row mismatch
    jnk = array([1,2])
    jnkf = join(outdir, 'jnk_regressor')
    jnk.tofile(jnkf, sep=' ', format = '%2.8f')
    assert_raises(IndexError, pydr.concat_regressors, a, jnkf)
    clean_tmpdir(outdir)

def test_template_timeseries_sub():
    datadir = get_data_dir()
    infile = join(datadir, 'test_B00-000_timeseries.nii.gz')
    template = join(datadir, 'test_template.nii.gz')
    mask = join(datadir, 'test_mask.nii.gz')
    outdir = tmp_outdir()
    outf = pydr.template_timeseries_sub(infile, template, mask, outdir)
    dat = loadtxt(outf)
    example = loadtxt(join(datadir, 'example_B00-000.txt'))
    
    assert_equal(True, (dat == example).all())
    clean_tmpdir(outdir)

def test_sub_spatial_map():
    datadir = get_data_dir()
    infile = join(datadir, 'test_B00-000_timeseries.nii.gz')
    template = join(datadir, 'test_template.nii.gz')
    mask = join(datadir, 'test_mask.nii.gz')
    outdir = tmp_outdir()
    sub_template_ts = join(datadir,  'example_B00-000.txt')
    tmap, zmap = pydr.sub_spatial_map(infile,
                                      sub_template_ts,
                                      mask, outdir)
    realt = join(datadir, 'example_B00-000.nii.gz')
    realz = join(datadir, 'example_B00-000_Z.nii.gz')

    assert_equal(ni.load(tmap).get_data(), ni.load(realt).get_data())
    assert_equal(ni.load(zmap).get_data(), ni.load(realz).get_data())
    
    clean_tmpdir(outdir)

def test_create_common_mask():
    datadir = get_data_dir()
    outdir = tmp_outdir()
    infile = join(datadir, 'test_B00-000_timeseries.nii.gz')
    realmask = join(datadir, 'example_mask.nii.gz')
    newmask = pydr.create_common_mask([infile,], outdir)
    assert_equal(ni.load(realmask).get_data(), ni.load(newmask).get_data())
    clean_tmpdir(outdir)
