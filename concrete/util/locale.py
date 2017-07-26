from __future__ import unicode_literals

import sys
import codecs


def set_stdout_encoding():
    '''
    Force stdout encoding to utf-8.  Ideally the user should set the
    output encoding to utf-8 (or otherwise) in their environment, as
    explained on the internet, but in practice it has been difficult
    to get that right (and scripts writing to stdout have broken).
    '''
    if sys.version_info[0] < 3:
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout)
    else:
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
