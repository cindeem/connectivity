# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:
import os, sys, re
from os.path import (abspath, join, dirname, exists)
from tempfile import mkdtemp
# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:
import os, sys, re
from os.path import (abspath, join, dirname, exists)
from tempfile import mkdtemp
import nibabel as ni
from unittest import TestCase, skipIf, skipUnless
from numpy.testing import (assert_raises, assert_equal, assert_almost_equal)
from numpy import (loadtxt, array)
from .. import matching as m

def get_data_dir():
    """ return directory holding data for tests"""
    testdir = os.path.dirname(__file__)
    moddir, _ = os.path.split(testdir)
    return join(moddir, 'ica', 'data')

def tmp_outdir():
    """ returns a temporary directory to store tests outputs"""
    return mkdtemp()

def clean_tmpdir(tmpdir):
    os.system('rm -rf %s'%tmpdir)



