from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup

setup(
    name = "concrete",
    version = "2.0.7pre",
    packages = [
        'concrete',
        'concrete.audio',
        'concrete.communication',
        'concrete.discourse',
        'concrete.email',
        'concrete.entities',
        'concrete.language',
        'concrete.metadata',
        'concrete.situations',
        'concrete.spans',
        'concrete.structure',
        'concrete.twitter',
        ],

    scripts = [
        'scripts/concrete2json.py',
        'scripts/validate_communication.py',
        ],

    test_suite = "tests",

    install_requires = [
        'networkx',
        'thrift>=0.9.1',
        ],

    url = "https://github.com/hltcoe/concrete",
    license="BSD",
)
