import glob
import os
import re
import sys

from setuptools import setup
from setuptools.command.install import install
from setuptools.command.test import test as TestCommand

metadata = dict(
    re.findall("__([a-z]+)__ = '([^']+)'", open('nomad_alt/nomad_version.py').read()))

requirements = [
    x.strip() for x
    in open('requirements.txt').readlines() if not x.startswith('#')]

description = "Alternative Python client for HashiCorp Nomad (http://www.nomadproject.io/)"

py_modules = [os.path.splitext(x)[0] for x in glob.glob('nomad_alt/*.py')]
py_modules.extend([os.path.splitext(x)[0] for x in glob.glob('nomad_alt/api/*.py')])


class Install(install):
    def run(self):
        # Issue #123: skip installation of nomad.aio if python version < 3.4.2
        # as this version or later is required by aiohttp
        if sys.version_info < (3, 4, 2):
            if 'nomad_alt/aio' in self.distribution.py_modules:
                self.distribution.py_modules.remove('nomad_alt/aio')
        install.run(self)


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)


setup(
    name='python-nomad_alt',
    version=metadata['version'],
    author='Aaron Tolman',
    author_email='TolmanAM@hotmail.com',
    url='git@github.com:tolmanam/python-nomad_alt.git',
    license='MIT',
    description=description,
    long_description=open('README.md').read() + '\n\n' +
                     open('CHANGELOG.rst').read(),
    py_modules=py_modules,
    install_requires=requirements,
    extras_require={
        'tornado': ['tornado'],
        'asyncio': ['aiohttp'],
        'twisted': ['twisted', 'treq'],
    },
    tests_require=['pytest', 'pytest-twisted'],
    cmdclass={'test': PyTest,
              'install': Install},
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
    ],
)
