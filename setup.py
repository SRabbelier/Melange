"""Minimal setup script to appease buildout for Melange.
"""
import os
import re
from setuptools import setup, find_packages

match_version = re.compile("version: ([0-9\-]+)")
try:
    appyaml = open(os.path.join("app", "app.yaml.template"))
    version = match_version.findall(appyaml.read())[0]
except:
    version = "UNKNOWN"


setup(
    name = 'melange',
    description=("The goal of this project is to create a framework for "
                 "representing Open Source contribution workflows, such as"
                 " the existing Google Summer of Code TM (GSoC) program."),
    version = version,
    packages = find_packages(exclude=['app.django.*','thirdparty','parts']),
    author=open("AUTHORS").read(),
    url='http://code.google.com/p/soc',
    license='Apache2',
    install_requires = [
        ],
    tests_require=[
        'zope.testbrowser',
        'gaeftest',
        'nose',
        ],
    entry_points = {'console_scripts': ['run-tests = tests.run:main',
                                        'gen-app-yaml = scripts.gen_app_yaml:main',
                                        ],
                    },
    include_package_data = True,
    zip_safe = False,
    )
