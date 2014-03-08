#!/usr/bin/python

"""
pyio_win32.py

Filesystem IO library.

Copyright (C) 2014  William Kettler <william.p.kettler@gmail.com>

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
import stat
import errno
from itertools import cycle
from math import ceil
from random import randint, shuffle
import win32file
import win32con

def seed(x):
    """
    Define a seed for the pseudo random number generator.

    Inputs:
        x (ANY): Random seed
    Outputs:
        NULL
    """
    random.seed(x)


def _samefile(src, dst):
    """
    Determine if src and dst are the same file.
    
    Inputs:
        src (str): Source file
        dst (str): Destination file
    Output:
        same (bool): Same file boolean
    """
    # Macintosh, Unix.
    if hasattr(os.path, 'samefile'):
        try:
            return os.path.samefile(src, dst)
        except OSError:
            return False

    # All other platforms: check for same pathname.
    return (os.path.normcase(os.path.abspath(src)) ==
            os.path.normcase(os.path.abspath(dst)))

def _blk_map(f, bs):
    """
    Build a block map index.
    
    Inputs:
        f  (str): File
        bs (int): Block size in KB
    Outputs:
        blk_map (list): List of block offsets
    """
    bs *= 1024
    
    # Get file size.
    sz = float(os.stat(f).st_size)
    
    # Build block map index.
    offsets = range(int(ceil(sz/bs)))
    blk_map = [offset * bs for offset in offsets]
    return blk_map

def mkdirs(d, mode=0777):
    """
    Create directory and intermediate directories if required.

    Input:
        d    (str): Directory
        mode (int): Permissions
    Outputs:
        NULL
    """
    try: 
        os.makedirs(d, mode)
    except OSError, err:
        # Reraise the error unless it's about an already existing directory 
        if err.errno != errno.EEXIST or not os.path.isdir(d): 
            raise
        
def w_zero(f, sz, bs, fsync=False):
    """
    Create a new file and fill it with zeros.

    Inputs:
        f      (str): File
        sz     (int): File size in KB
        bs     (int): Block size in KB
        fsync (bool): Fsync after IO is complete
    Outputs:
        NULL
    """
    pass

def w_srand(f, sz, bs, fsync=False):
    """
    Create a new file and fill it with pseudo random data.
    
    Inputs:
        f      (str): File
        sz     (int): File size in KB
        bs     (int): Block size in KB
        fsync (bool): Fsync after IO is complete
    Outputs:
        NULL
    """
    pass

def w_rand(f, sz, bs, fsync=False):
    """
    Create a new file and fill it with random data.
    
    Inputs:
        f      (str): File
        sz     (int): File size in KB
        bs     (int): Block size in KB
        fsync (bool): Fsync after IO is complete
    Outputs:
        NULL
    """
    pass

def w_rand_blk(f, bs, fsync=False):
    """
    Seek to a random offset and write random data of specified block size.
    
    Note that there is no way to modify the middle of a file without first
    reading the entire file, modifying the contents, and re-writing the file. 
    Because we simply want to write to a random location the file will be 
    truncated based on the loaction of the random seek and update.
    
    Inputs:
        f      (str): File
        bs     (int): Block size in KB
        fsync (bool): Fsync after IO is complete
    Outputs:
        NULL
    """
    pass

def cp(src, dst, bs, fsync=False):
    """
    Copy a file from source to destination.
    
    The destination may be a directory.
    
    Inputs:
        src    (str): Source file
        dst    (str): Destination file or directory
        bs     (int): Block size in KB
        fsync (bool): Fsync after IO is complete
    Outputs:
        NULL
    """
    bs *= 1024
   
    if os.path.isdir(dst):
        dst = os.path.join(dst, os.path.basename(src))
   
    # Open destination file using win32 API
    fdst = win32file.CreateFile(dst, win32file.GENERIC_WRITE, 0, None,
           win32con.CREATE_ALWAYS, None, None)

    try:
        # Write file and metadata.
        with open(src, 'rb') as fsrc:
            while True:
                buf = fsrc.read(bs)
                if not buf:
                    break
                win32file.WriteFile(fdst, buf)
    
        # Flush and close dst
        if fsync:
            win32file.FlushFileBuffers(fdst)
    except:
        raise
    finally:
        fdst.close()
            
def cp_conv(src, dst, bs, fsync=False):
    """
    Converge file copy. Given a file of size 's' a converged copy
    will copy the blocks at offset 0, s - bs, bs, s - 2*bs, and so 
    on converging to the middle of the file until the entire file has
    been copied.
        
    The destination may be a directory.
    
    Inputs:
        src    (str): Source file
        dst    (str): Destination file or directory
        bs     (int): Block size in KB
        fsync (bool): Fsync after IO is complete
    Outputs:
        NULL
    """ 
    pass

def cp_rand(src, dst, bs, fsync=False):
    """
    Copy a file from source to destination using random IO. A file
    block map is built and random offsets are selected and copied
    until the entire file been written to the destination.
    
    The destination may be a directory.
    
    Inputs:
        src    (str): Source file
        dst    (str): Destination file or directory
        bs     (int): Block size in KB
        fsync (bool): Fsync after IO is complete
    Outputs:
        NULL
    """
    pass
    
def r_seq(f, bs):
    """
    Sequential file read.
    
    Inputs:
        f  (str): File
        bs (int): Block size in KB
    Outputs:
        NULL
    """
    pass
   
def r_rand(f, bs):
    """
    Read a file using random IO.
    
    Inputs:
        f  (str): File
        bs (int): Block size in KB
    Outputs:
        NULL
    """
    pass
    
def r_conv(f, bs):
    """
    Converge file read. Given a file of size s a converged read
    will read the blocks at offset 0, sz - bs, bs, sz - 2*bs, and so 
    on converging to the middle of the file until the entire file has
    been read.
    
    Inputs:
        f  (str): File
        bs (int): Block size in KB
    Outputs:
        NULL
    """
    pass

def r_rand_blk(f, bs):
    """
    Read a random block of specified block size.
    
    Inputs:
        f  (str): File
        bs (int): Block size in KB
    Outputs:
        NULL
    """
    pass