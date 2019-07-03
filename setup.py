# -*- coding: utf-8 -*-
from setuptools import setup

setup(
    name='python-smartgadget',
    version='0.1.0',
    packages=['sensirionbt'],
    python_requires='>=3.4',
    install_requires=['bluepy>=1.0.5'],
    description='Library for reading temperature, humidity, and battery level from a '
                'SHT31 Smart Gadget Development Kit by Sensirion',
    author='Matthias Erll',
    author_email='matthias@erll.de',
    url='https://github.com/merll/python-smartgadget',
    license="MIT",
)
