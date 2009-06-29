
import sys
import subprocess

import tzinfo
import domSupport

LOG_ENTRY_TEMPLATE = """\
------------------------------------------------------------------------
r%(revision)s | %(author)s | %(date)s

%(message)s
"""

VERBOSE_TEMPLATE = """\
------------------------------------------------------------------------
r%(revision)s | %(author)s | %(date)s
Changed paths:
%(paths)s
%(message)s
"""

PR_TEMPLATE = """\
%(revision)s - %(message)s
"""

CHANGED_PATH_TEMPLATE = """\
   %(action)s %(path)s
"""

import codecs, locale
unicodeOutput = codecs.getwriter(locale.getpreferredencoding())(sys.stdout)

def _formatChangedPaths(logEntry):
    changes = []
    for pathNode in logEntry.getElementsByTagName("path"):
        model = {
            "action": pathNode.getAttribute("action"),
            "path": domSupport.getText(pathNode),
            }
        changes.append(CHANGED_PATH_TEMPLATE % model)
    changes.sort()
    return "".join(changes)

def _reformatDate(dateTime):
    utcDate = domSupport.parseDateTime(dateTime)
    utcDate = utcDate.replace(tzinfo=tzinfo.utc)
    localDate = utcDate.astimezone(tzinfo.Local)
    return localDate.ctime()

def outputEntries(xentries, options):
    for entry in xentries:
        _outputLogEntry(entry, options)

def _outputLogEntry(logEntry, options):
    revision = logEntry.getAttribute("revision")
    author = domSupport.getChildText(logEntry, "author")
    dateValue = domSupport.getChildText(logEntry, "date")
    dateValue = _reformatDate(dateValue)

    template = LOG_ENTRY_TEMPLATE
    if options.verbose > 0:
        template = VERBOSE_TEMPLATE
    if options.pr:
        template = PR_TEMPLATE

    model = {
            "revision": revision,
            "author": author,
            "message": domSupport.getChildText(logEntry, "msg"),
            "date": dateValue,
            "paths": _formatChangedPaths(logEntry),
            }
    unicodeOutput.write(template % model)
    if options.verbose > 1:
        sys.stdout.write(_getDiff(revision))

def _getDiff(revision):
    args = ["svn", "diff", "-c", revision]
    popen = subprocess.Popen(args=args, stdout=subprocess.PIPE,
            shell=False)
    return popen.stdout.read()

