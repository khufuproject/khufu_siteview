import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
CHANGES = open(os.path.join(here, 'CHANGES.rst')).read()

requires = [
    'setuptools',
    'pyramid',
    'pyramid_jinja2',
    'Paste',
    ]

setup(name='khufu_templview',
      version='0.1',
      description='Easy template-to-view support',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
        ],
      license='BSD',
      author='Rocky Burt',
      author_email='rocky@serverzen.com',
      url='https://github.com/serverzen/khufu_templview',
      keywords='pyramid khufu',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      test_suite="khufu_templview.tests",
      )
