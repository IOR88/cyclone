from setuptools import setup
import os


def _get_version():
    filename = os.path.join('src', 'cyclone', '__init__.py')
    glb = {}
    with open(filename) as fp:
        for line in fp:
            if '__version__' in line:
                exec(line, glb)
                return glb['__version__']
    raise RuntimeError('cannot find version')

setup(
    name='cyclone',
    version=_get_version(),
    description='Cyclone',
    namespace_packages=[],
    package_dir={'': 'src'},
    packages=[
        'cyclone',
        'cyclone.spiders'

    ],
    include_package_data=True,
    install_requires=[
        'SQLAlchemy==1.3.1  ',
        'beautifulsoup4==4.7.1',
        'scrapy==1.6.0',
        'psycopg2==2.7.7'
    ]
)