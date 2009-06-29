
import re
import datetime

def getChild(node, elementName):
    """ Returns the first element under that name or None.
    """
    for child in node.childNodes:
        if (child.nodeType == child.ELEMENT_NODE
                and child.tagName == elementName):
            return child
    return None

def getChildElements(node, elementName):
    """ Returns all child elements with the given name.
    """
    kids = []
    for child in node.childNodes:
        if (child.nodeType == child.ELEMENT_NODE
                and child.tagName == elementName):
            kids.append(child)
    return kids

def getText(node):
    text = ""
    for child in node.childNodes:
        if child.nodeType == child.TEXT_NODE:
            text += child.data
    return text

def getChildText(node, elementName):
    """ Returns value stored inside the named element.
    @return text or None
    """
    element = getChild(node, elementName)
    if element is None:
        return None
    return getText(element)


def getAllText(node):
    text = ""
    for child in node.childNodes:
        if child.nodeType == child.TEXT_NODE:
            text += child.data
        else:
            text += getAllText(child)
    return text

FLOAT_NUMBER = r"-?[0-9]+(?:\.[0-9]+)?"
DURATION_PATTERN = re.compile(r"P(?P<years>%sY)?(?P<months>%sM)?(?P<days>%sD)?T?(?P<hours>%sH)?(?P<minutes>%sM)?(?P<seconds>%sS)?" % (6 * (FLOAT_NUMBER,)))

def parseDuration(value):
    """ Parses XML Schema duration datetype:
    http://www.w3.org/TR/xmlschema-2/#duration
    Value example: "PT1H50M0S"
    Returns dict {"years":years, "months":months, ...}
    """
    match = DURATION_PATTERN.match(value)
    if not match:
        raise ValueError("Bad duration: %r" % value)
    numbers = {}
    for key, found in match.groupdict().iteritems():
        if found is None:
            numbers[key] = 0
        else:
            # Strips the designator char
            numbers[key] = float(found[:-1])
    return numbers

DATETIME_PATTERN = re.compile(r"(\d+)-(\d+)-(\d+)T(\d+):(\d+):(\d+)(?:\.\d+)?Z?$")

def parseDateTime(value):
    """ Parses subset of XML Schema dateTime:
    Value example: "2007-07-30T03:30:00"
    Returns datetime.datetime.
    """
    match = DATETIME_PATTERN.match(value)
    if match is None:
        raise ValueError("Invalid dateTime value: '%s'" % value)
    numbers = []
    for group in match.groups():
        numbers.append(int(group))
    return datetime.datetime(*numbers)

