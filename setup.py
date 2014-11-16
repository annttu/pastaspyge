from codecs import open
from setuptools import setup, find_packages


# Get the long description from the relevant file
with open('README', encoding='utf-8') as f:
    long_description = f.read()


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
