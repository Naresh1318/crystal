from setuptools import setup
import os
import sys

_here = os.path.abspath(os.path.dirname(__file__))

if sys.version_info[0] < 3:
    with open(os.path.join(_here, 'README.md')) as f:
        long_description = f.read()
else:
    with open(os.path.join(_here, 'README.md'), encoding='utf-8') as f:
        long_description = f.read()

setup(name='crystal',
      version='0.1.0',
      description='A realtime plotting library built using plot.ly',
      long_description=long_description,
      long_description_content_type='text/markdown',
      keywords='plotting charts realtime',
      url='https://github.com/Naresh1318/crystal',
      author='Naresh Nagabushan',
      author_email='nnaresh@vt.edu',
      licence='MIT',
      packages=['crystal'],
      python_requires='>=3',
      zip_safe=False,
      install_requires=[
            'numpy',
            'Flask==1.0.2'
      ],
      include_package_data=True,
      classifiers=[
            'Development Status :: 3 - Alpha',
            'Intended Audience :: Science/Research',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3.6'],
      scripts=['bin/crystal'])
