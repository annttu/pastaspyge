from codecs import open
import pypandoc
from setuptools import setup, find_packages

description = "Thin wrapper for pandoc."
try:
    long_description = pypandoc.convert('README.md', 'rst')
except (IOError, OSError):
    print('check that you have installed pandoc properly and that README.md exists!')
    long_description = "Static web page generator."



setup(name='pastaspyge',
      version='0.1',
      description="Static web page generator.",
      long_description=long_description,
      classifiers=[],
      keywords='web',
      author='Antti Jaakkola',
      author_email='pastaspyge@annttu.fi',
      url='https://github.com/annttu/pastaspyge',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      install_requires=[],
      extras_require={
          'test': ['pytest']
      }
      )
