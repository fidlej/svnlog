#!/usr/bin/env python
"""\
Usage: %prog PATH_OLD PATH_NEw
Compares the two paths recursively.
Permissions, ownership and content are compared.
"""
from __future__ import with_statement

import optparse
import os
import stat
import sys

def _parse_args():
    parser = optparse.OptionParser()
    parser.add_option("-v", "--verbose", action="count", dest="verbosity",
            help="increase verbosity")
    parser.set_defaults(verbosity=0)

    options, args = parser.parse_args()
    if len(args) != 2:
        parser.error("Specify two paths to compare!")

    return options, args

class Comparator(object):
    COMPARED_STATS = (
            "st_mode",
            "st_uid",
            "st_gid",
            "st_rdev",
            "st_size"
            )

    def xchanges(self, old, new):
        """Generates the changes as (flag, old_path, new_path) pairs.
        The flag could be A, D or M_...
        for added, delete or modified files.
        """
        old_stat = os.lstat(old)
        new_stat = os.lstat(new)
        if not _equal_stat(old_stat, new_stat, self.COMPARED_STATS):
            yield ("M_stat", old, new)
            return

        if not stat.S_ISDIR(old_stat.st_mode):
            if stat.S_ISLNK(old_stat.st_mode):
                if not _equal_links(old, new):
                    yield ("M_link", old, new)
            else:
                if not _equal_content(old, new):
                    yield ("M_content", old, new)
        else:
            for change in self._compare_tree(old, new):
                yield change

    def _compare_tree(self, old, new):
        old_set = frozenset(os.listdir(old))
        new_set = frozenset(os.listdir(new))

        only_old = old_set - new_set
        only_new = new_set - old_set
        both = old_set & new_set

        for name in sorted(only_old):
            yield ("D", os.path.join(old, name), None)

        for name in sorted(only_new):
            yield ("A", None, os.path.join(new, name))

        for name in sorted(both):
            for change in self.xchanges(
                    os.path.join(old, name),
                    os.path.join(new, name)):
                yield change

def _equal_stat(old_stat, new_stat, compared_stats):
    for member in compared_stats:
        old_value = getattr(old_stat, member, None)
        new_value = getattr(new_stat, member, None)
        if old_value != new_value:
            return False
    return True

def _equal_links(old_path, new_path):
    return os.readlink(old_path) == os.readlink(new_path)

def _equal_content(old_path, new_path):
    """Compares the content of the two files.
    """
    # Code derived from filecmp.py.
    # Copyright (c) 2001, 2002, 2003, 2004, 2005, 2006 Python Software Foundation; All Rights Reserved
    bufsize = 8 * 1024
    with open(old_path, 'rb') as fp1:
      with open(new_path, 'rb') as fp2:
        while True:
            b1 = fp1.read(bufsize)
            b2 = fp2.read(bufsize)
            if b1 != b2:
                return False
            if not b1:
                return True

def _format_change(change, compared_stats, verbosity=0):
    flag, old, new = change
    if flag == "A":
        _format_extra_file(new)
    elif flag == "D":
        _format_extra_file(old)
    else:
        print "Files %s and %s differ" % (old, new)
        if verbosity > 0:
            if flag == "M_stat":
                print _diff_stat(old, new, compared_stats)
            elif flag == "M_link":
                print _diff_link(old, new)

def _format_extra_file(path):
    print "Only in %s: %s" % (os.path.dirname(path), os.path.basename(path))

def _diff_stat(old, new, compared_stats):
    old_stat = os.lstat(old)
    new_stat = os.lstat(new)
    output = ""
    for member in compared_stats:
        if member == "st_size" and stat.S_ISDIR(old_stat.st_mode):
            continue
        if member == "st_mode" and stat.S_ISLNK(old_stat.st_mode):
            continue

        old_value = getattr(old_stat, member, None)
        new_value = getattr(new_stat, member, None)
        if old_value != new_value:
            output += " %s: %r != %r\n" % (member, old_value, new_value)
    return output

def _diff_link(old, new):
    return " link: %s != %s\n" % (os.readlink(old), os.readlink(new))


def main():
    options, args = _parse_args()
    old, new = args
    returncode = 0
    comparator = Comparator()
    for change in comparator.xchanges(old, new):
        returncode = 1
        _format_change(change, comparator.COMPARED_STATS, options.verbosity)

    sys.exit(returncode)

if __name__ == "__main__":
    main()

