#!/usr/bin/env python
"""\
Usage: %prog [options] -- [extra_svn_args]
Prints filtered SVN changelog.
"""

import logging
import optparse
import subprocess
import xml.dom.pulldom
import xml.parsers.expat
import os
import signal
import errno

import formatting
import filtering

def parseArgs():
    parser = optparse.OptionParser(usage=__doc__)
    parser.add_option("-l", "--limit", type="int",
            help="limit the number of log entries")
    parser.add_option("-m", "--message",
            help="filter by regex for a message")
    parser.add_option("-a", "--authors",
            help="filter by authors")
    parser.add_option("-D", "--date",
            help="filter by date")
    parser.add_option("-v", "--verbose", action="count",
            help="increase the verboseness")
    parser.add_option("--pr", action="store_true",
            help="output just revision numbers")

    options, args = parser.parse_args()
    if options.authors:
        options.authors = options.authors.split(",")

    return options, args

def getSvnLogFile(options, extra_args):
    args = ["svn", "log", "--xml", "-rHEAD:0"]
    if options.verbose > 0:
        args.append("--verbose")
    args += extra_args

    popen = subprocess.Popen(args=args, stdout=subprocess.PIPE,
            shell=False, close_fds=True)
    return popen.stdout, popen.pid

def generateLogEntries(svnLogFile):
    try:
        reader = xml.dom.pulldom.parse(svnLogFile)
        for event, node in reader:
            if event == "START_ELEMENT" and node.tagName == "logentry":
                reader.expandNode(node)
                yield node
    except IOError, (no, str):
        if no == errno.EPIPE:
            logging.warn(str)
            return
        raise

def main():
    options, args = parseArgs()
    logging.debug("Options: %s", options)
    svnLogFile, svnPid = getSvnLogFile(options, args)

    xentries = generateLogEntries(svnLogFile)
    xentries = filtering.filter(xentries, options)
    formatting.outputEntries(xentries, options)

    os.kill(svnPid, signal.SIGKILL)

if __name__ == "__main__":
    logging.root.setLevel(logging.DEBUG)
    main()
