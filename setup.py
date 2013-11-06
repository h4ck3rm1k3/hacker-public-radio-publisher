"""
setup
"""

from setuptools import setup, find_packages
setup(
    name = "HackerPublicRadioPublisher",
    version = "0.1",
    description = "Python Uploader for Hacker Public Radio",
    long_description=u'''
    A set of scripts to manage the creation and uploading of shows into HPR
    ''',
    platforms = "Debian GNU/Linux",
    author = "James Michael DuPont",
    author_email = "jamesmikedupont@gmail.com",
    license = "GNU GPLv3",
    url = "github.com/h4ck3rm1k3/hacker-public-radio-publisher",


    packages = find_packages(),
     package_data = {
         '': ['*.txt', '*.flac', '*.html'],
    },
    install_requires =
    [
        'nose',
        'ftputil>=2.8',
        'internetarchive>=0.4.4',
        'Jinja>=1.2',
        'PyYAML>=3.10',
        'docopt>=0.6.1',
        'pytest>=2.3.4',
        'jsonpatch>=1.1',
        'requests>=2.0.0',
#        'requests>=1.2.0',
        'py>=1.4.14',
        'jsonpointer>=1.1',
        #'audiotools',
        #not working with pip,
        # get code from : https://github.com/tuffy/python-audio-tools.git

                    ],

    test_suite = 'nose.collector'
)
