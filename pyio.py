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
from random import randint, shuffle, seed
try:
    import win32file
    import win32con
except:
    pass

def _seed(x):
    """
    Define a seed for the pseudo random number generator.

    Inputs:
        x (ANY): Random seed
    Outputs:
        NULL
    """
    seed(x)


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
    st = os.stat(f)
    sz = float(st.st_size)
    
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
    
    with open(f, 'wb') as fh:
        while True:
            if sz < bs:
                fh.write(buf * sz)
                break
            fh.write(buf * bs)
            sz -= bs
        # Force write of fdst to disk.
        if fsync:
            fh.flush()
            os.fsync(fh.fileno())

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
    
    with open(f, 'wb') as fh:
        while True:
            if sz < bs:
                fh.write(buf * sz)
                break
            fh.write(buf * bs)
            sz -= bs
        # Force write of fdst to disk.
        if fsync:
            fh.flush()
            os.fsync(fh.fileno())

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
    
    with open(f, 'wb') as fh:
        while True:
            if sz < bs:
                buf = os.urandom(sz)
                fh.write(buf)
                break
            buf = os.urandom(bs)
            fh.write(buf)
            sz -= bs
        # Force write of fdst to disk.
        if fsync:
            fh.flush()
            os.fsync(fh.fileno())

def w_rand_blk(f, bs, fsync=False):
    """
    Seek to a random offset and write random data of specified block size.
    
    Inputs:
        f      (str): File
        bs     (int): Block size in KB
        fsync (bool): Fsync after IO is complete
    Outputs:
        NULL
    """
    sz = os.stat(f).st_size
    bs *= 1024
    if sz < bs:
        raise ValueError('block size is greater than file size')
    buf = os.urandom(1024) * bs / 1024
    
    with open(f, 'r+b') as fh:
        offset = randint(0, sz - bs)
        fh.seek(offset)
        buf = fh.write(buf)
        # Force write of fdst to disk.
        if fsync:
            fh.flush()
            os.fsync(fh.fileno())

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

    # Write file.
    with open(src, 'rb') as fsrc:
        with open(dst, 'wb') as fdst:
            while True:
                buf = fsrc.read(bs)
                if not buf:
                    break
                fdst.write(buf)
            # Force write of fdst to disk.
            if fsync:
                fdst.flush()
                os.fsync(fdst.fileno())
            
def cp_conv(src, dst, bs, fsync=False):
    """
    Converge file copy.
        
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

    # Copy file.
    idx = cycle([0,-1]).next
    with open(src, 'rb') as fsrc:
        with open(dst, 'wb') as fdst:
            while blk_map:
                offset = blk_map.pop(idx())
                fsrc.seek(offset)
                fdst.seek(offset)
                buf = fsrc.read(bs)
                fdst.write(buf)
            # Force write of fdst to disk.
            if fsync:
                fdst.flush()
                os.fsync(fdst.fileno())

def cp_rand(src, dst, bs, fsync=False):
    """
    Copy a file from source to destination using random IO.
    
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
    with open(src, 'rb') as fsrc:
        with open(dst, 'wb') as fdst:
            while blk_map:
                offset = blk_map.pop()
                fsrc.seek(offset)
                fdst.seek(offset)
                buf = fsrc.read(bs)
                fdst.write(buf)
            # Force write of fdst to disk.
            if fsync:
                fdst.flush()
                os.fsync(fdst.fileno())
                
def cp_win32(src, dst, bs, fsync=False):
    """
    Copy a file from source to destination using the win32 libraries.
    
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

    # Write file and metadata.
    with open(f, 'rb') as fh:
        while True:
            buf = fh.read(bs)
            if not buf:
                break
   
def r_rand(f, bs):
    """
    Random file read.
    
    Inputs:
        f  (str): File
        bs (int): Block size in KB
    Outputs:
        NULL
    """
    blk_map = _blk_map(src, bs)
    bs *= 1024
    
    shuffle(blk_map)
    with open(src, 'rb') as fsrc:
        while blk_map:
            offset = blk_map.pop()
            fsrc.seek(offset)
            fsrc.read(bs)
    
def r_conv(f, bs):
    """
    Converge file read.
    
    Inputs:
        f  (str): File
        bs (int): Block size in KB
    Outputs:
        NULL
    """
    blk_map = _blk_map(src, bs)
    bs *= 1024
    
    idx = cycle([0,-1]).next
    with open(f, 'rb') as fh:
        while blk_map:
            offset = blk_map.pop(idx())
            fh.seek(offset)
            fh.read(bs)

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
    st = os.stat(f)
    sz = st.st_size
    offset = randint(0, sz - bs)
            
    with open(f, 'rb') as fh:
        fh.seek(offset)
        fh.read(bs)