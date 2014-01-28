#!/usr/bin/python

"""
pyio.py

Filesystem IO library.

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
import stat
import errno
from itertools import cycle
from math import ceil
from random import randint, shuffle

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
    buf = '\0' * 1024
    
    try:
        fh = os.open(f, os.O_CREAT | os.O_TRUNC | os.O_WRONLY)
        while True:
            if sz < bs:
                os.write(fh, buf * sz)
                break
            os.write(fh, buf * bs)
            sz -= bs
        # Force write of fdst to disk.
        if fsync:
            os.fsync(fh)
    except:
        raise
    finally:
        os.close(fh)

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
    buf = os.urandom(1024)
    
    try:
        fh = os.open(f, os.O_CREAT | os.O_TRUNC | os.O_WRONLY)
        while True:
            if sz < bs:
                os.write(fh, buf * sz)
                break
            os.write(fh, buf * bs)
            sz -= bs
        # Force write of fdst to disk.
        if fsync:
            os.fsync(fh)
    except:
        raise
    finally:
        os.close(fh)

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
    bs *= 1024
    sz *= 1024
    
    try:
        fh = os.open(f, os.O_CREAT | os.O_TRUNC | os.O_WRONLY)
        while True:
            if sz < bs:
                buf = os.urandom(sz)
                os.write(fh, buf)
                break
            buf = os.urandom(bs)
            os.write(fh, buf)
            sz -= bs
        # Force write of fdst to disk.
        if fsync:
            os.fsync(fh)
    except:
        raise
    finally:
        os.close(fh)

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
    sz = os.stat(f).st_size
    buf = os.urandom(1024) * bs
    bs *= 1024
    if sz < bs:
        raise ValueError('block size is greater than file size')
    
    try:
        fh = os.open(f, os.O_CREAT | os.O_TRUNC | os.O_WRONLY)
        os.lseek(fh, randint(0, sz - bs), 0)
        os.write(fh, buf)
        # Force write of fdst to disk.
        if fsync:
            os.fsync(fh)
    except:
        raise
    finally:
        os.close(fh)

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
    if os.path.isdir(dst):
        dst = os.path.join(dst, os.path.basename(src)) 
    if _samefile(src, dst):
        raise Error("`%s` and `%s` are the same file" % (src, dst))
    bs *= 1024

    try:
        fsrc = os.open(src, os.O_RDONLY)
        fdst = os.open(dst, os.O_CREAT | os.O_TRUNC | os.O_WRONLY)
        while True:
            buf = os.read(fsrc, bs)
            if not buf:
                break
            os.write(fdst, buf)
        # Force write of fdst to disk.
        if fsync:
            os.fsync(fdst)
    except:
        raise
    finally:
        os.close(fsrc)
        os.close(fdst)
            
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
    if os.path.isdir(dst):
        dst = os.path.join(dst, os.path.basename(src))
    if _samefile(src, dst):
        raise Error("`%s` and `%s` are the same file" % (src, dst))   
    blk_map = _blk_map(src, bs)
    bs *= 1024
    idx = cycle([0,-1]).next

    try:
        fsrc = os.open(src, os.O_RDONLY)
        fdst = os.open(dst, os.O_CREAT | os.O_TRUNC | os.O_WRONLY)
        while blk_map:
            offset = blk_map.pop(idx())
            os.lseek(fsrc, offset, 0)
            os.lseek(fdst, offset, 0)
            buf = os.read(fsrc, bs)
            os.write(fdst, buf)
        # Force write of fdst to disk.
        if fsync:
            os.fsync(fdst)
    except:
        raise
    finally:
        os.close(fsrc)
        os.close(fdst)

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
    if os.path.isdir(dst):
        dst = os.path.join(dst, os.path.basename(src))
    if _samefile(src, dst):
        raise Error("`%s` and `%s` are the same file" % (src, dst))
    
    blk_map = _blk_map(src, bs)
    bs *= 1024
    shuffle(blk_map)
    
    try:
        fsrc = os.open(src, os.O_RDONLY)
        fdst = os.open(dst, os.O_CREAT | os.O_TRUNC | os.O_WRONLY)
        while blk_map:
            offset = blk_map.pop()
            os.lseek(fsrc, offset, 0)
            os.lseek(fdst, offset, 0)
            buf = os.read(fsrc, bs)
            os.write(fdst, buf)
        # Force write of fdst to disk.
        if fsync:
            os.fsync(fdst)
    except:
        raise
    finally:
        os.close(fsrc)
        os.close(fdst)
    
def r_seq(f, bs):
    """
    Sequential file read.
    
    Inputs:
        f  (str): File
        bs (int): Block size in KB
    Outputs:
        NULL
    """
    bs *= 1024

    try:
        fh = os.open(f, os.O_RDONLY)
        while True:
            buf = os.read(fh, bs)
            if not buf:
                break
    except:
        raise
    finally:
        os.close(fh)
   
def r_rand(f, bs):
    """
    Read a file using random IO.
    
    Inputs:
        f  (str): File
        bs (int): Block size in KB
    Outputs:
        NULL
    """
    blk_map = _blk_map(f, bs)
    bs *= 1024
    shuffle(blk_map)
    
    try:
        fh = os.open(f, os.O_RDONLY)
        while blk_map:
            offset = blk_map.pop()
            os.lseek(fh, offset, 0)
            os.read(fh, bs)
    except:
        raise
    finally:
        os.close(fh)
    
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
    blk_map = _blk_map(f, bs)
    bs *= 1024
    idx = cycle([0,-1]).next
    
    try:
        fh = os.open(f, os.O_RDONLY)
        while blk_map:
            offset = blk_map.pop(idx())
            os.lseek(fh, offset, 0)
            os.read(fh, bs)
    except:
        raise
    finally:
        os.close(fh)

def r_rand_blk(f, bs):
    """
    Read a random block of specified block size.
    
    Inputs:
        f  (str): File
        bs (int): Block size in KB
    Outputs:
        NULL
    """
    bs *= 1024
    sz = os.stat(f).st_size
    if sz < bs:
        raise ValueError('block size is greater than file size')
    
    try:            
        fh = os.open(f, os.O_RDONLY)
        os.lseek(fh, randint(0, sz - bs), 0)
        os.read(fh, bs)
    except:
        raise
    finally:
        os.close(fh)