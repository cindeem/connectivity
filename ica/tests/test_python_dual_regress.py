# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:
import os, sys, re
from os.path import (abspath, join, dirname, exists)
from unittest import TestCase, skipIf, skipUnless
from numpy.testing import (assert_raises, assert_equal)
from .. import python_dual_regress as pydr

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
    subid = get_subid(instr)
    assert_equal(subid, sid)
