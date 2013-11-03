from setuptools import setup, find_packages
setup(
    name = "HackerPublicRadioPublisher",
    version = "0.1",
    packages = find_packages(),
     package_data = {
         '': ['*.txt', '*.flac', '*.html'],
    },
    install_requires = [
        'jinja',
        'internetarchive',
        'audiotools',
        'ftputil',
                    ],
) 
