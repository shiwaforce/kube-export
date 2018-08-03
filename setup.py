#!/usr/bin/env python
import kubexport
import sys
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

requires = ['docopt==0.6.2']
test_requires = ['pytest==3.7.1', 'pytest-cov==2.5.1']

if sys.version_info[0] < 3:
    test_requires.append('SystemIO>=1.1')

class PyTestCommand(TestCommand):
    """Run py.test unit tests"""

    def finaalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = ['--verbose', '--cov', 'kubexport']
        self.test_suite = True

    def run(self):
        import pytest
        rcode = pytest.main(self.test_args)
        sys.exit(rcode)

setup_options = dict(
    name='kubexport',
    version=kubexport.__version__,
    description='Kubernetes export tool. Export Kubernetes resources in structured  yaml or json files.',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    author='Shiwaforce.com',
    url='https://www.shiwaforce.com',
    packages=find_packages(exclude=['tests*']),
    install_requires=requires,
    tests_require=test_requires,
    cmdclass={'test': PyTestCommand},
    entry_points={
      'console_scripts': ['kube-export=kubexport.kubexport:main'],
    },
    license="MIT",
    classifiers=(
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Natural Language :: English',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ),
)

setup(**setup_options)