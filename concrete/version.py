from __future__ import unicode_literals

__version__ = '4.13.0'


def concrete_library_version():
    return __version__


def concrete_schema_version():
    return '.'.join(__version__.split('.')[0:2])


def add_argparse_argument(parser):
    from .util.thrift_factory import is_accelerated
    parser.add_argument(
        '--version', action='version',
        version='concrete-python %s (schema %s) (%s)' % (
            concrete_library_version(),
            concrete_schema_version(),
            'accelerated' if is_accelerated() else 'unaccelerated'
        )
    )
