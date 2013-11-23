#!/usr/bin/python

"""
r_loop.py

Infinite read loop.

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

import os
import argparse
from random import randint
from pyio import r_seq

def walk(root):
    """
    Walk directory and return absolute path for all files.
    
    Inputs:
        root (str): Root directory
    Outputs:
        f (list): List of files
    """
    if not os.path.isdir(root):
        raise ValueError('%s is not a directory' % root)
    
    f = []
    for root, dirs, files in os.walk(root):
        for name in files:
            f.append(os.path.join(root, name))
    return f

def main(root, bs):
    """
    Infinite read loop.
    
    Inputs:
        root (str): Root directory
        bs   (int): Block size in KB
    Outputs:
        NA
    """
    
    # Walk directory
    files = walk(root)
    
    while True:
        x = randint(0, len(files)-1)
        f = files[x]
        print 'Reading "f".'
        r_seq(f, bs)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Infinite read loop.')
    parser.add_argument('--dir', '-d', dest='dir', type=str, required=True,
                    help='Root directory')
    parser.add_argument('--bs', dest='bs', type=int, required=False, default=32,
                    help='IO block size in KB')
    args = parser.parse_args()
    main(args.dir, args.bs)