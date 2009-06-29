
import time
import domSupport

def filterByAuthors(xentries, authors):
    authors = set(authors)
    for logEntry in xentries:
        author = domSupport.getChildText(logEntry, "author")
        if author in authors:
            yield logEntry

def filterByMessage(xentries, messageRegex):
    import re
    pattern = re.compile(messageRegex)
    for entry in xentries:
        msg = domSupport.getChildText(entry, "msg")
        if pattern.search(msg) is not None:
            yield entry

def filterByDate(xentries, date):
    """Keeps just entries with the given date.
    It is more robust then the -r {date}:{date+1}.
    """
    if date == "today":
        date = time.strftime("%Y-%m-%d", time.localtime())

    for entry in xentries:
        loggedDate = domSupport.getChildText(entry, "date")
        if loggedDate.startswith(date):
            yield entry
        elif loggedDate < date:
            return

def filterByLimit(xentries, limit):
    import itertools
    return itertools.islice(xentries, limit)

FILTERS = (
        ("authors", filterByAuthors),
        ("message", filterByMessage),
        ("date", filterByDate),
        ("limit", filterByLimit),
        )

def filter(xentries, options):
    for key, filter_fn in FILTERS:
        value = getattr(options, key)
        if value is None:
            continue

        xentries = filter_fn(xentries, value)

    return xentries
