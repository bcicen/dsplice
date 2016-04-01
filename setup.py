import os
import sys
from setuptools import setup

exec(open('dsplice/version.py').read())

setup(name='dsplice',
      version=version,
      packages=['dsplice'],
      description='Docker image merge tool',
      author='Bradley Cicenas',
      author_email='bradley@vektor.nyc',
      url='https://github.com/bcicen/dsplice',
      install_requires=['docker-py>=1.7.2'],
      license='http://opensource.org/licenses/MIT',
      classifiers=(
          'License :: OSI Approved :: MIT License ',
          'Natural Language :: English',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 3',
      ),
      keywords='docker image merge devops',
      entry_points = {
        'console_scripts' : ['dsplice = dsplice.cli:main']
      }
      )
