#!/usr/bin/python

"""
ut.py

Unit test.

Copyright (C) 2013  William Kettler <william.p.kettler@gmail.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the 
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import pyio
import filecmp

# Test directory
d = 'ut/test'

# mkdirs
pyio.mkdirs(d)

# w_zero
pyio.w_zero('%s/zero_1.out' % d, 10, 32, fsync=False)
pyio.w_zero('%s/zero_2.out'% d, 10, 1, fsync=True)

# w_srand
pyio.w_srand('%s/srand_1.out' % d, 10, 32, fsync=False)
pyio.w_srand('%s/srand_2.out'% d, 32, 1, fsync=True)

# w_rand
pyio.w_rand('%s/rand_1.out' % d, 10, 32, fsync=False)
pyio.w_rand('%s/rand_2.out'% d, 32, 1, fsync=True)

# w_rand_blk
pyio.w_zero('%s/rand_blk_1.out' % d, 32, 64, fsync=False)
try:
    pyio.w_rand_blk('%s/rand_blk_1.out' % d, 128, fsync=False)
except ValueError:
    pass
pyio.w_zero('%s/rand_blk_2.out' % d, 32, 32, fsync=False)
pyio.w_rand_blk('%s/rand_blk_2.out' % d, 8, fsync=True)

# cp
pyio.cp('%s/srand_1.out' % d, '%s/cp_srand_1.out' % d, 1, fsync=False)
if not filecmp.cmp('%s/srand_1.out' % d, '%s/cp_srand_1.out' % d):
    print 'pyio.cp round 1 files differ'
pyio.cp('%s/srand_2.out' % d, '%s/cp_srand_2.out' % d, 32, fsync=True)
if not filecmp.cmp('%s/srand_2.out' % d, '%s/cp_srand_2.out' % d):
    print 'pyio.cp round 2 files differ'

# cp_conv
pyio.cp_conv('%s/rand_1.out' % d, '%s/cp_rand_1.out' % d, 1, fsync=False)
if not filecmp.cmp('%s/rand_1.out' % d, '%s/cp_rand_1.out' % d):
    print 'pyio.cp_conv round 1 files differ'
pyio.cp_conv('%s/rand_2.out' % d, '%s/cp_rand_2.out' % d, 64, fsync=True)
if not filecmp.cmp('%s/rand_2.out' % d, '%s/cp_rand_2.out' % d):
    print 'pyio.cp_conv round 2 files differ'

# cp_rand
pyio.cp_rand('%s/rand_blk_1.out' % d, '%s/cp_rand_blk_1.out' % d, 32, fsync=False)
if not filecmp.cmp('%s/rand_blk_1.out' % d, '%s/cp_rand_blk_1.out' % d):
    print 'pyio.cp_rand round 1 files differ'
pyio.cp_rand('%s/rand_blk_2.out' % d, '%s/cp_rand_blk_2.out' % d, 128, fsync=True)
if not filecmp.cmp('%s/rand_blk_2.out' % d, '%s/cp_rand_blk_2.out' % d):
    print 'pyio.cp_rand round 2 files differ'
    
# r_seq
pyio.r_seq('%s/zero_1.out' % d, 8)
pyio.r_seq('%s/zero_1.out' % d, 128)

# r_rand
pyio.r_rand('%s/zero_1.out' % d, 8)
pyio.r_rand('%s/zero_1.out' % d, 128)

# r_conv
pyio.r_conv('%s/zero_1.out' % d, 8)
pyio.r_conv('%s/zero_1.out' % d, 128)

# r_rand_blk
pyio.r_rand_blk('%s/zero_1.out' % d, 8)
try:
    pyio.r_rand_blk('%s/zero_1.out' % d, 128)
except ValueError:
    pass