from setuptools import setup, find_packages

import campbot

setup(
    name='campbot',
    version=campbot.__version__,
    packages=find_packages(),
    author="Charles de Beauchesne",
    author_email="charles.de.beauchesne@gmail.com",
    description="Package for automatic edition of camptocamp.org",
    long_description=open('README.md').read(),

    install_requires=["requests", "python-dateutil", "pytz"],

    include_package_data=True,

    url='http://github.com/cbeauchesne/CampBot',

    classifiers=[
        "Programming Language :: Python",
        "Development Status :: 1 - Planning",
        "License :: OSI Approved",
        "Natural Language :: French",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.5",
        "Topic :: Communications",
    ],

    entry_points={
        'console_scripts': [
            'campbot = campbot.__main__',
        ],
    },

    license="WTFPL",

)