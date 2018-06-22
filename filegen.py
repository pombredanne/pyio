#!/usr/bin/env python

"""
filegen.py

File generation utility.

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
import sys
import time
from random import randint
from argparse import ArgumentParser
from lib.pyio import w_srand, w_rand, w_zero


def mkdir(dir):
    """
    Make a directory if it doesn't already exist.

    Inputs:
        dir (str): Directory name
    Outputs:
        None
    """
    if not os.path.exists(dir):
        os.mkdir(dir)


def filegen(min_sz, max_sz, qty, ftype, bs=1024, dst=None, split=None):
    """
    Generate files.

    Inputs:
        min_sz (int): Minimum file size
        max_sz (int): Maximum file size
        qty    (int): Total file count
        ftype  (int): File type
        dst    (str): Destination directory
        split  (int): File per directory
    Outputs:
        NULL
    """
    # Define file type
    if ftype == 0:
        print 'Using the zero file generator.'
        ftype_str = "zero"
        gen = lambda f, size, bs: w_zero(f, size, bs)
    elif ftype == 1:
        print 'Using the random file generator.'
        ftype_str = "random"
        gen = lambda f, size, bs: w_rand(f, size, bs)
    elif ftype == 2:
        print 'Using the pseudo-random file generator.'
        ftype_str = "srandom"
        gen = lambda f, size, bs: w_srand(f, size, bs)
    else:
        raise RuntimeError('Invalid file type.')

    # Use current directory if not defined
    if not dst:
        dst = os.getcwd()

    if split:
        current_dir = 0
        pwd = os.path.join(dst, str(current_dir))
        mkdir(pwd)
    else:
        current_dir = dst
        pwd = dst
        split = qty

    dir_ct = 0
    global_ct = 0
    global_size = 0
    while True:
        stime = time.time()
        while dir_ct < split:
            # Write file.
            size = randint(min_sz, max_sz)
            f = os.path.join(pwd, ".".join([ftype_str, str(dir_ct)]))
            gen(f, size, bs)

            # Update counters
            dir_ct += 1
            global_size += size
            global_ct += 1

            # Write update
            sys.stdout.write("\r")
            sys.stdout.write("The current file count is: %s" % global_ct)
            sys.stdout.flush()

            # Exit if file count limit reached
            if global_ct == qty:
                etime = time.time()
                tput = global_size / (etime - stime)
                print ""
                print "Wrote %s files at %s KB/s" % (global_ct, tput)
                print "Complete!"
                return

        # Create new working directory
        current_dir += 1
        pwd = os.path.join(dst, str(current_dir))
        mkdir(pwd)

        # Reset directory file count
        dir_ct = 0

if __name__ == '__main__':
    # Define CLI arguments.
    parser = ArgumentParser(description='File generation utility.')
    parser.add_argument('--min', dest='min', type=int, required=True,
                        help='minimum file size in KB')
    parser.add_argument('--max', dest='max', type=int, required=True,
                        help='max file size in KB')
    parser.add_argument('--qty', dest='qty', type=int, required=False,
                        default=-1, help='file count, default is infinite')
    parser.add_argument('--ftype', '-f', dest='ftype', type=int, required=True,
                        choices=[0, 1, 2],
                        help='file type (0=zero, 1=rand, 2=srand)')
    parser.add_argument('--dst', dest='dst', type=str, required=False,
                        default=None, help='destination directory')
    parser.add_argument('--split', dest='split', type=int, required=False,
                        default=None, help='files per directory')
    parser.add_argument('--bs', dest='bs', type=int, required=False,
                        default=1024, help='IO record size')
    args = parser.parse_args()

    try:
        filegen(args.min, args.max, args.qty, args.ftype, args.bs, args.dst,
                args.split)
    except KeyboardInterrupt:
        print ""
        sys.exit("Killed by user.")
