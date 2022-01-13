# -*- coding: utf-8 -*-
#######################################################################
# License: MIT License                                                #
# Homepage: https://github.com/tasooshi/footrecon/                    #
# Version: 0.2                                                        #
#######################################################################

import setuptools


with open('README.md') as f:
    long_description = f.read()


setuptools.setup(
    name='footrecon',
    version='0.2',
    author='tasooshi',
    author_email='tasooshi@pm.me',
    description='A mobile all-in-one solution for physical recon',
    license='MIT License',
    keywords=[
        'redteaming',
        'scanner',
        'discovery',
    ],
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/tasooshi/footrecon/',
    packages=setuptools.find_packages(),
    install_requires=(
        'asciimatics==1.13.0',
        'cffi==1.15.0',
        'future==0.18.2',
        'gps==3.19',
        'imageio-ffmpeg==0.4.5',
        'imageio==2.12.0',
        'numpy==1.21.4',
        'Pillow==9.0.0',
        'PyBluez==0.23',
        'pyfiglet==0.8.post1',
        'sounddevice==0.4.3',
        'SoundFile==0.10.3.post1',
        'wcwidth==0.2.5',
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
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ]
)
