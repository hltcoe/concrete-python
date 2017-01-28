from __future__ import unicode_literals

import sys
import codecs


def set_stdout_encoding():
    if sys.version_info[0] < 3:
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout)
    else:
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
