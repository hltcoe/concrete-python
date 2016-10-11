__version__ = '4.10.8'


def concrete_library_version():
    return __version__


def concrete_schema_version():
    return ".".join(__version__.split(".")[0:2])


def add_argparse_argument(parser):
    parser.add_argument("--version", action="version",
                        version=("Concrete schema version: %s, "
                                 "Concrete python library version: %s") %
                                (concrete_schema_version(),
                                 concrete_library_version()))
