#!/usr/bin/env python

"""
pyio.py

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
import errno
import random
from itertools import cycle
from math import ceil


def seed(x):
    """
    Define a seed for the pseudo random number generator.

    Args:
        x (ANY): Random seed
    """
    random.seed(x)


def _samefile(src, dst):
    """
    Determine if src and dst are the same file.

    Args:
        src (str): Source file
        dst (str): Destination file
    Returns:
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


def _blk_map(fname, blksz):
    """
    Build a block map index.

    Args:
        fname (str): File name
        blksz (int): Block size in KB
    Returns:
        blk_map (list): List of block offsets
    """
    blksz *= 1024

    # Get file size.
    size = float(os.stat(fname).st_size)

    # Build block map index.
    offsets = range(int(ceil(size/blksz)))
    blk_map = [offset * blksz for offset in offsets]
    return blk_map


def mkdirs(dname, mode=0777):
    """
    Create directory and intermediate directories if required.

    Args:
        dname (str): Directory name
        mode (int): Permissions
    """
    try:
        os.makedirs(dname, mode)
    except OSError, err:
        # Reraise the error unless it's about an already existing directory
        if err.errno != errno.EEXIST or not os.path.isdir(dname):
            raise


def w_zero(fname, size, blksz, fsync=False):
    """
    Create a new file and fill it with zeros.

    Args:
        fname (str): File name
        size (int): File size in KB
        blksz (int): Block size in KB
        fsync (bool): Fsync after IO is complete
    """
    buf = '\0' * 1024

    fd = os.open(fname, os.O_CREAT | os.O_TRUNC | os.O_WRONLY)
    try:
        while True:
            if size < blksz:
                os.write(fd, buf * size)
                break
            os.write(fd, buf * blksz)
            size -= blksz
        # Force write of fd to disk
        if fsync:
            os.fsync(fd)
    except:
        raise
    finally:
        os.close(fd)


def w_srand(fname, size, blksz, fsync=False):
    """
    Create a new file and fill it with pseudo random data.

    Args:
        fname (str): File name
        size (int): File size in KB
        blksz (int): Block size in KB
        fsync (bool): Fsync after IO is complete
    """
    buf = os.urandom(1024)

    fd = os.open(fname, os.O_CREAT | os.O_TRUNC | os.O_WRONLY)
    try:
        while True:
            if size < blksz:
                os.write(fd, buf * size)
                break
            os.write(fd, buf * blksz)
            size -= blksz
        # Force write of fd to disk
        if fsync:
            os.fsync(fd)
    except:
        raise
    finally:
        os.close(fd)


def w_rand(fname, size, blksz, fsync=False):
    """
    Create a new file and fill it with random data.

    Args:
        fname (str): File name
        size (int): File size in KB
        blksz (int): Block size in KB
        fsync (bool): Fsync after IO is complete
    """
    blksz *= 1024
    size *= 1024

    fd = os.open(fname, os.O_CREAT | os.O_TRUNC | os.O_WRONLY)
    try:
        while True:
            if size < blksz:
                buf = os.urandom(size)
                os.write(fd, buf)
                break
            buf = os.urandom(blksz)
            os.write(fd, buf)
            size -= blksz
        # Force write of fd to disk
        if fsync:
            os.fsync(fd)
    except:
        raise
    finally:
        os.close(fd)


def w_rand_blk(fname, blksz, fsync=False):
    """
    Seek to a random offset and write random data of specified block size.

    Note that there is no way to modify the middle of a file without first
    reading the entire file, modifying the contents, and re-writing the file.
    Because we simply want to write to a random location the file will be
    truncated based on the loaction of the random seek and update.

    Args:
        fname (str): File name
        blksz (int): Block size in KB
        fsync (bool): Fsync after IO is complete
    """
    size = os.stat(fname).st_size
    buf = os.urandom(1024) * blksz
    blksz *= 1024
    if size < blksz:
        raise ValueError('block size is greater than file size')

    fd = os.open(fname, os.O_CREAT | os.O_TRUNC | os.O_WRONLY)
    try:
        os.lseek(fd, random.randint(0, size - blksz), 0)
        os.write(fd, buf)
        # Force write of fd to disk
        if fsync:
            os.fsync(fd)
    except:
        raise
    finally:
        os.close(fd)


def cp(src, dst, blksz, fsync=False):
    """
    Copy a file from source to destination.

    The destination may be a directory.

    Args:
        src (str): Source file
        dst (str): Destination file or directory
        blksz (int): Block size in KB
        fsync (bool): Fsync after IO is complete
    """
    if os.path.isdir(dst):
        dst = os.path.join(dst, os.path.basename(src))
    if _samefile(src, dst):
        raise Exception("`%s` and `%s` are the same file" % (src, dst))
    blksz *= 1024

    # Handles the scenario where fdsrc opens but fddst fails.
    # The fdsrc file is successfully closed if fddst fails to open
    fdsrc = os.open(src, os.O_RDONLY)
    try:
        fddst = os.open(dst, os.O_CREAT | os.O_TRUNC | os.O_WRONLY)
    except:
        os.close(fdsrc)
        raise

    # Perform the copy
    try:
        while True:
            buf = os.read(fdsrc, blksz)
            if not buf:
                break
            os.write(fddst, buf)
        # Force write of fddst to disk
        if fsync:
            os.fsync(fddst)
    except:
        raise
    finally:
        os.close(fdsrc)
        os.close(fddst)


def cp_conv(src, dst, blksz, fsync=False):
    """
    Converge file copy. Given a file of size 's' a converged copy
    will copy the blocks at offset 0, s - blksz, blksz, s - 2*blksz, and so
    on converging to the middle of the file until the entire file has
    been copied.

    The destination may be a directory.

    Args:
        src (str): Source file
        dst (str): Destination file or directory
        blksz (int): Block size in KB
        fsync (bool): Fsync after IO is complete
    """
    if os.path.isdir(dst):
        dst = os.path.join(dst, os.path.basename(src))
    if _samefile(src, dst):
        raise Exception("`%s` and `%s` are the same file" % (src, dst))
    blk_map = _blk_map(src, blksz)
    blksz *= 1024
    idx = cycle([0, -1]).next

    # Handles the scenario where fdsrc opens but fddst fails.
    # The fdsrc file is successfully closed if fddst fails to open
    fdsrc = os.open(src, os.O_RDONLY)
    try:
        fddst = os.open(dst, os.O_CREAT | os.O_TRUNC | os.O_WRONLY)
    except:
        os.close(fdsrc)
        raise

    # Perform the copy
    try:
        while blk_map:
            offset = blk_map.pop(idx())
            os.lseek(fdsrc, offset, 0)
            os.lseek(fddst, offset, 0)
            buf = os.read(fdsrc, blksz)
            os.write(fddst, buf)
        # Force write of fddst to disk
        if fsync:
            os.fsync(fddst)
    except:
        raise
    finally:
        os.close(fdsrc)
        os.close(fddst)


def cp_rand(src, dst, blksz, fsync=False):
    """
    Copy a file from source to destination using random IO. A file
    block map is built and random offsets are selected and copied
    until the entire file been written to the destination.

    The destination may be a directory.

    Args:
        src (str): Source file
        dst (str): Destination file or directory
        blksz (int): Block size in KB
        fsync (bool): Fsync after IO is complete
    """
    if os.path.isdir(dst):
        dst = os.path.join(dst, os.path.basename(src))
    if _samefile(src, dst):
        raise Exception("`%s` and `%s` are the same file" % (src, dst))

    blk_map = _blk_map(src, blksz)
    blksz *= 1024
    random.shuffle(blk_map)

    # Handles the scenario where fdsrc opens but fddst fails.
    # The fdsrc file is successfully closed if fddst fails to open
    fdsrc = os.open(src, os.O_RDONLY)
    try:
        fddst = os.open(dst, os.O_CREAT | os.O_TRUNC | os.O_WRONLY)
    except:
        os.close(fdsrc)
        raise

    # Perform the copy
    try:
        while blk_map:
            offset = blk_map.pop()
            os.lseek(fdsrc, offset, 0)
            os.lseek(fddst, offset, 0)
            buf = os.read(fdsrc, blksz)
            os.write(fddst, buf)
        # Force write of fddst to disk
        if fsync:
            os.fsync(fddst)
    except:
        raise
    finally:
        os.close(fdsrc)
        os.close(fddst)


def r_seq(fname, blksz):
    """
    Sequential file read.

    Args:
        fname (str): File name
        blksz (int): Block size in KB
    """
    blksz *= 1024

    fd = os.open(fname, os.O_RDONLY)
    try:
        while True:
            buf = os.read(fd, blksz)
            if not buf:
                break
    except:
        raise
    finally:
        os.close(fd)


def r_rand(fname, blksz):
    """
    Read a file using random IO.

    Args:
        fname (str): File name
        blksz (int): Block size in KB
    """
    blk_map = _blk_map(fname, blksz)
    blksz *= 1024
    random.shuffle(blk_map)

    fd = os.open(fname, os.O_RDONLY)
    try:
        while blk_map:
            offset = blk_map.pop()
            os.lseek(fd, offset, 0)
            os.read(fd, blksz)
    except:
        raise
    finally:
        os.close(fd)


def r_conv(fname, blksz):
    """
    Converge file read. Given a file of size sz, a converged read
    will read the blocks at offset 0, size - blksz, blksz, size - 2*blksz,
    and so on converging to the middle of the file until the entire file has
    been read.

    Args:
        fname (str): File name
        blksz (int): Block size in KB
    """
    blk_map = _blk_map(fname, blksz)
    blksz *= 1024
    idx = cycle([0, -1]).next

    fd = os.open(fname, os.O_RDONLY)
    try:
        while blk_map:
            offset = blk_map.pop(idx())
            os.lseek(fd, offset, 0)
            os.read(fd, blksz)
    except:
        raise
    finally:
        os.close(fd)


def r_rand_blk(fname, blksz):
    """
    Read a random block of specified block size.

    Args:
        fname (str): File name
        blksz (int): Block size in KB
    """
    blksz *= 1024
    size = os.stat(fname).st_size
    if size < blksz:
        raise ValueError('block size is greater than file size')

    fd = os.open(fname, os.O_RDONLY)
    try:
        os.lseek(fd, random.randint(0, size - blksz), 0)
        os.read(fd, blksz)
    except:
        raise
    finally:
        os.close(fd)
