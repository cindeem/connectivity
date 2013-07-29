# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:
import os, sys, re
from os.path import (abspath, join, dirname, exists)
from tempfile import mkdtemp
#import nibabel as ni
from unittest import TestCase, skipIf, skipUnless
from numpy.testing import (assert_raises, assert_equal, assert_almost_equal)
from numpy import (loadtxt, array, concatenate)
from numpy import random

from .. import calc_scan_durations as csd

class TestCalcScanDurations(TestCase):
    def setUp(self):
        prng = random.RandomState(42)
        self.data = prng.rand(100)

    def test_demean(self):
        res = self.data - self.data.mean()
        demeaned = csd.demean(self.data)
        assert_almost_equal(res.mean(), demeaned.mean())



