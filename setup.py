from setuptools import setup

setup(
    name = "concrete",
    version = "2.0.5pre",
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

    install_requires = ['thrift>=0.9.1'],

    url = "https://github.com/hltcoe/concrete",
    license="BSD",
)
