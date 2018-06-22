#!/usr/bin/env python

"""
r_all.py

Read all files in a give directory.

Copyright (C) 2017  William Kettler <william.p.kettler@gmail.com>

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
import threading
import argparse
import scandir


def walk(directory):
    """
    A generator that walks a directory and returns the relative path to all
    files.

    Args:
        directory (str): Directory path
    """
    if not os.path.isdir(directory):
        raise ValueError('%s is not a directory' % directory)

    for root, dirs, files in scandir.walk(directory):
        for name in files:
            yield os.path.join(root, name)


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


def read_thr(queue, blocksz, lock):
    """
    Simple thread that retrieves a file off the queue and reads the first
    byte.

    Args:
        queue (iterator): An iterator containing file paths
        blocksz (int): Block size
        lock (threading.Lock): A lock used to control access to the queue
    """
    print threading.currentThread().getName(), 'Starting\n',
    while True:
        with lock:
            try:
                fname = queue.next()
            except StopIteration:
                print threading.currentThread().getName(), 'Exiting\n',
                return
        #print threading.currentThread().getName(), fname
        r_seq(fname, blocksz)


def main():
    """
    Main function.
    """
    parser = argparse.ArgumentParser(description='Read all files in a given'
                                     'directory')
    parser.add_argument('-d', '--dir', type=str, required=True,
                        dest='directory', help='directory to walk')
    parser.add_argument('-t', '--threadct', type=int, required=True,
                        dest='threadct', help='thread count')
    parser.add_argument('--bs', '--blocksz', type=int, required=True,
                        dest='blocksz', help='block size in KB')
    args = parser.parse_args()

    # Init the queue and lock
    queue = walk(args.directory)
    lock = threading.Lock()

    # Start the threads
    threads = []
    for i in range(args.threadct+1):
        t = threading.Thread(target=read_thr, args=(queue, args.blocksz,
                                                    lock,))
        threads.append(t)
        t.start()

    # Wait until all threads return
    for t in threads:
        t.join()

if __name__ == "__main__":
    main()
