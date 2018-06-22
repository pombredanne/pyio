#!/usr/bin/env python

"""
tree.py

Create a directory tree.

Copyright (c) 2014  William Kettler <william.p.kettler@gmail.com>

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with
this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import os
from pyio import mkdirs


def tree(width, depth, dst):
    """
    Created a nested directory structure.

    Inputs:
        width (int): Directory width
        depth (int): Directory depth
        dst   (str): Destination
    Outputs:
        None
    """
    prev_dirs = [dst]
    for d in range(depth):
        cur_dirs = []
        for prev_dir in prev_dirs:
            for w in range(width):
                cur_dir = os.path.join(prev_dir, str(w))
                mkdirs(cur_dir)
                cur_dirs.append(cur_dir)

        prev_dirs = cur_dirs
