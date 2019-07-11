from distutils.spawn import find_executable
import os

from setuptools import setup


def include_readme():
    try:
        import pandoc
    except ImportError:
        return ''
    pandoc.core.PANDOC_PATH = find_executable('pandoc')
    readme_file = os.path.join(os.path.dirname(__file__), 'README.md')
    doc = pandoc.Document()
    with open(readme_file, 'r') as rf:
        doc.markdown = rf.read()
    return doc.rst.decode('utf-8')


setup(
    name='python-smartgadget',
    version='0.1.0',
    packages=['sensirionbt'],
    python_requires='>=3.4',
    install_requires=['bluepy>=1.0.5'],
    description='Library for reading temperature, humidity, and battery level from a '
                'SHT31 Smart Gadget Development Kit by Sensirion',
    long_description=include_readme(),
    author='Matthias Erll',
    author_email='matthias@erll.de',
    url='https://github.com/merll/python-smartgadget',
    license="MIT",
)
