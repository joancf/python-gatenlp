"""
Various utilities that could be useful in several modules.
"""
import numbers
import sys
import os
import logging
import datetime
import time
from functools import wraps


def match_substrings(text, items, getstr=None, cmp=None, unmatched=False):
    """
    Matches each item from the items sequence with sum substring of the text
    in a greedy fashion. An item is either already a string or getstr is used
    to retrieve a string from it. The text and substrings are normally
    compared with normal string equality but cmp can be replaced with
    a two-argument function that does the comparison instead.
    This function expects that all items are present in the text, in their order
    and without overlapping! If this is not the case, an exception is raised.

    Args:
      text: the text to use for matching
      items: items that are or contains substrings to match
      getstr: a function that retrieves the text from an item (Default value = None)
      cmp: a function that compares to strings and returns a boolean \
    that indicates if they should be considered to be equal. (Default value = None)
      unmatched: if true returns two lists of tuples, where the second list\
    contains the offsets of text not matched by the items (Default value = False)

    Returns:
      a list of tuples (start, end, item) where start and end are the\
      start and end offsets of a substring in the text and item is the item for that substring.

    """
    if getstr is None:
        getstr = lambda x: x
    if cmp is None:
        cmp = lambda x,y: x == y
    ltxt = len(text)
    ret = []
    ret2 = []
    item_idx = 0
    start = 0
    lastunmatched = 0
    while start < ltxt:
        itemorig = items[item_idx]
        item = getstr(itemorig)
        end = start + len(item)
        if end > ltxt:
            raise Exception("Text too short to match next item: {}".format(item))
        if cmp(text[start:end], item):
            if unmatched and start > lastunmatched:
                ret2.append((lastunmatched, start))
                lastunmatched = start + len(item)
            ret.append((start, end, itemorig))
            start += len(item)
            item_idx += 1
            if item_idx == len(items):
                break
        else:
            start += 1
    if item_idx != len(items):
        raise Exception("Not all items matched but {} of {}".format(item_idx, len(items)))
    if unmatched and lastunmatched != ltxt:
        ret2.append((lastunmatched, ltxt))
    if unmatched:
        return ret, ret2
    else:
        return ret


logger = None
start = 0


def set_logger(name=None, file=None, lvl=None, args=None):
    """
    Set up logger for the module "name". If file is given, log to that file as well.
    If file is not given but args is given and has "outpref" parameter, log to
    file "outpref.DATETIME.log" as well.

    Args:
        name: name to use in the log, if None, uses sys.argv[0]
        file: if given, log to this destination in addition to stderr
        lvl: set logging level
        args: not used yet

    Returns:
        The logger instance
    """
    global logger
    if name is None:
        name = sys.argv[0]
    if logger:
        raise Exception("Odd, we should not have a logger yet?")
    logger = logging.getLogger(name)
    if lvl is None:
        lvl = logging.INFO
    logger.setLevel(lvl)
    fmt = logging.Formatter('%(asctime)s|%(levelname)s|%(name)s|%(message)s')
    hndlr = logging.StreamHandler(sys.stderr)
    hndlr.setFormatter(fmt)
    logger.addHandler(hndlr)
    if file:
        hdnlr = logging.FileHandler(file)
        hndlr.setFormatter(fmt)
        logger.addHandler(hdnlr)
    logger.info("Started: {}".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M%S")))
    return logger


def ensurelogger():
    """
    Make sure the global logger is set to some logger. This should not be necessary
    if the set_logger function is properly used, but guards against situations where
    functions that require a logger are used without proper setting up the logger.

    Returns:
        A logger instance.
    """
    global logger
    if not logger:
        logger = logging.getLogger("UNINITIALIZEDLOGGER")
    return logger


def run_start():
    """
    Define time when running starts.

    Returns:
        system time in seconds
    """
    global  start
    start = time.time()
    return start


def run_stop():
    """
    Log and return formatted elapsed run time.

    Returns:
        tuple of formatted run time, run time in seconds
    """
    logger = ensurelogger()
    if start == 0:
        logger.warning("Run timing not set up properly, no time!")
        return "",0
    stop = time.time()
    delta = stop - start
    deltastr = str(datetime.timedelta(seconds=delta))
    logger.info(f"Runtime: {deltastr}")
    return deltastr, delta


def file4logger(thelogger, noext=False):
    """
    Return the first logging file found for this logger or None if there is no file handler.

    Args:
        thelogger: logger

    Returns:
        file path (string)
    """
    lpath = None
    for h in thelogger.handlers:
        if isinstance(h, logging.FileHandler):
            lpath = h.baseFilename
            if noext:
                lpath = os.path.splitext(lpath)[0]
            break
    return lpath


def support_annotation_or_set(method):
    """
    Decorator to allow a method that normally takes a start and end
    offset to take an annotation or annotation set, or any other object that has
    "start" and "end" attributes, or a pair of offsets instead.
    It also allows to take a single offset instead which will then be used
    to create a length one span (start is the original offset, end is the original offset plus one)

    Args:
      method: the method that gets converted by this decorator.

    Returns:
        the adapted method which now takes an annotation or annotation set as well as start/end offsets.
    """
    @wraps(method)
    def _support_annotation_or_set(self, *args, **kwargs):
        from gatenlp.annotation import Annotation
        annid = None
        if len(args) == 1:
            obj = args[0]
            if hasattr(obj, "start") and hasattr(obj, "end"):
                left, right = obj.start, obj.end
            elif isinstance(obj, (tuple, list)) and len(obj) == 2:
                left, right = obj
            elif isinstance(obj, numbers.Integral):
                left, right = obj, obj+1
            else:
                raise Exception("Not an annotation or an annotation set or pair: {}".format(args[0]))
            if isinstance(obj, Annotation):
                annid = obj.id
        else:
            assert len(args) == 2
            left, right = args
        # if the called method/function does have an annid keyword, pass it, otherwise omit
        if "annid" in method.__code__.co_varnames:
            return method(self, left, right, annid=annid, **kwargs)
        else:
            return method(self, left, right, **kwargs)

    return _support_annotation_or_set
