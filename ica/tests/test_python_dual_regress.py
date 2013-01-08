# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:
import os, sys, re
from os.path import (abspath, join, dirname, exists)
from tempfile import mkdtemp
import nibabel as ni
from unittest import TestCase, skipIf, skipUnless
from numpy.testing import (assert_raises, assert_equal, assert_almost_equal)
from numpy import (loadtxt, array)
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
    template_timeseries_sub = join(datadir,  'example_B00-000.txt')
    tmap, zmap = pydr.sub_spatial_map(infile,
                                      template_timeseries_sub,
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
