from __future__ import unicode_literals


def lun(l):
    '''
    If l is None return an empty list, else return l.
    Simplifies iteration over list fields that might be unset.

    Args:
        l (list): input list (or None)

    Return
        l, or an empty list if l is None
    '''
    return list() if (l is None) else l


def dun(d):
    '''
    If l is None return an empty dict, else return l.
    Simplifies iteration over dict fields that might be unset.

    Args:
        d (dict): input dict (or None)

    Return
        d, or an empty dict if d is None
    '''
    return dict() if (d is None) else d


def sun(s):
    '''
    If l is None return an empty set, else return l.
    Simplifies iteration over set fields that might be unset.

    Args:
        s (set): input set (or None)

    Return
        s, or an empty set if s is None
    '''
    return set() if (s is None) else s
