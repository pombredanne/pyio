#!/usr/bin/env python

"""
dd.py

A Python wrapper for the GNU dd command utility.

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

from execute import execute

def dd(ifile, ofile, bs, count=None):
    """
    Wrapper for the GNU dd command.

    Inputs:
        ifile (str): Input file
        ofile (str): Output file
        bs    (str): Block size
        count (int): Number of blocks to copy
    Outputs:
        time (float): Duration
        tput (float): Throughput in B/s
        iops (float): IOPS
    """
    # Execute dd command
    if count is  not None:
        cmd = "dd if=%s of=%s bs=%s count=%i" % (ifile, ofile, bs, count)
    else:
        cmd = "dd if=%s of=%s bs=%s" % (ifile, ofile, bs)

    try:
        stdout, stderr = execute(cmd)
    except:
        raise

    # Split lines into fields
    records_in, records_out, summary = stderr.split('\n')

    # Parse for record counts
    # If we run out of disk space requested vs actual will vary
    s = re.search(r"^([0-9]*)\+.*", records_in)
    records_in = int(s.group(1))
    s = re.search(r"^([0-9]*)\+.*", records_out)
    records_out = int(s.group(1))

    # There is no reason the record counts should not match but if they
    # do raise an exception because it will effect calculations.
    if records_in != records_out:
        raise Exception('records mismatch')

    # Parse for the byte total and time
    s = re.search(r"^([0-9]*).*([0-9]+\.[0-9]+) s", summary)
    size = int(s.group(1))
    time = float(s.group(2))

    # Calculate throughput in Mib, i.e. base 2
    # Note that dd returns base 10 calcaulation
    tput = size / time

    # Calculate IOPS
    iops = records_in / time

    return (time, tput, iops)

def w_seq(f, bs, count):
    """
    Sequential write.

    Inputs:
        f     (str): File
        bs    (int): Block size
        count (int): Block count
    Outputs:
        time (float): Time
        tput (float): Throughput in B/s
        iops (float): IO's per second
    """
    time, tput, iops = dd('/dev/zero', f, bs, count)
    return (time, tput, iops)

def r_seq(f, bs):
    """
    Sequential read.

    Inputs:
        f (str): File
        bs (int): Block size in KB
    Outputs:
        time (float): Time
        tput (float): Throughput in B/s
        iops (float): IO's per second
    """
    time, tput, iops = dd(f, 'dev/null', bs)
    return (time, tput, iops)