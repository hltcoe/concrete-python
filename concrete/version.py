__version__ = '4.12.4'


def concrete_library_version():
    return __version__


def concrete_schema_version():
    return '.'.join(__version__.split('.')[0:2])


def add_argparse_argument(parser):
    from concrete.util.thrift_factory import is_accelerated
    parser.add_argument(
        '--version', action='version',
        version='concrete-python %s (schema %s) (%s)' % (
            concrete_library_version(),
            concrete_schema_version(),
            'accelerated' if is_accelerated() else 'unaccelerated'
        )
    )
