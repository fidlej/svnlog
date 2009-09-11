
import time
import domSupport
import logging

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
    mode = "startswith"
    op = unicode.startswith
    if date and date[0] in "><":
        mode = date[0]
        date = date[1:]
        op = unicode.__gt__ if mode == ">" else unicode.__lt__

    try:
        offset_days = int(date)
    except ValueError:
        pass
    else:
        offset_seconds = offset_days * 3600 * 24
        date = time.strftime("%Y-%m-%d",
                time.localtime(time.time() + offset_seconds))

    logging.debug("Filtering by date: %s %s", mode, date)
    for entry in xentries:
        loggedDate = domSupport.getChildText(entry, "date")
        if op(loggedDate, date):
            yield entry
        elif mode != "<" and loggedDate < date:
            return

def filterByLimit(xentries, limit):
    import itertools
    return itertools.islice(xentries, limit)

FILTERS = (
        ("date", filterByDate),
        ("authors", filterByAuthors),
        ("message", filterByMessage),
        ("limit", filterByLimit),
        )

def filter(xentries, options):
    for key, filter_fn in FILTERS:
        value = getattr(options, key)
        if value is None:
            continue

        xentries = filter_fn(xentries, value)

    return xentries
