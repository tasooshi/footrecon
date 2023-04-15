# -*- coding: utf-8 -*-
#######################################################################
# License: MIT License                                                #
# Homepage: https://github.com/tasooshi/footrecon/                    #
#######################################################################

import pathlib
import setuptools


def from_file(*names, encoding='utf8'):
    return pathlib.Path(
        pathlib.Path(__file__).parent, *names
    ).read_text(encoding=encoding)


version = {}
contents = pathlib.Path('src/footrecon/version.py').read_text()
exec(contents, version)


setuptools.setup(
    name='footrecon',
    version=version['__version__'],
    author='tasooshi',
    author_email='tasooshi@pm.me',
    description='A mobile all-in-one solution for physical recon',
    license='MIT License',
    keywords=[
        'redteaming',
        'scanner',
        'wardriving',
        'discovery',
    ],
    long_description=from_file('README.md'),
    long_description_content_type='text/markdown',
    url='https://github.com/tasooshi/footrecon/',
    packages=setuptools.find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    install_requires=(
        'asciimatics==1.14.0',
        'cffi==1.15.1',
        'imageio-ffmpeg==0.4.8',
        'imageio==2.27.0',
        'numpy==1.24.2',
        'Pillow==9.5.0',
        'PyBluez@git+https://github.com/pybluez/pybluez.git#egg=pybluez',
        'pyfiglet==0.8.post1',
        'sounddevice==0.4.6',
        'SoundFile==0.12.1',
        'wcwidth==0.2.6',
    ),
    zip_safe=False,
    entry_points={
        'console_scripts': (
            'footrecon=footrecon.core.app:entry_point',
        ),
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Topic :: Utilities',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ]
)
