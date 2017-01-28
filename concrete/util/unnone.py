from __future__ import unicode_literals


def lun(l):
    '''
    If l is None return an empty list, else return l.
    Simplifies iteration over list fields that might be unset.
    '''
    return list() if (l is None) else l


def dun(d):
    '''
    If l is None return an empty dict, else return l.
    Simplifies iteration over dict fields that might be unset.
    '''
    return dict() if (d is None) else d


def sun(s):
    '''
    If l is None return an empty set, else return l.
    Simplifies iteration over set fields that might be unset.
    '''
    return set() if (s is None) else s
