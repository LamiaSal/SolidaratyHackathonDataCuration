"""
setup
"""
from setuptools import find_packages, setup
import os

with open("README.md", "r", encoding="utf-8") as fp:
    long_description = fp.read()

with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = []
    for req in f.readlines():
        if req[0] == "\ufeff":
            req = req[1:]
        req = req[:-1]
        requirements.append(req)

setup(
    name="src",
    version="0.0.0",
    # package_dir={"": "src"},
    packages=find_packages(where="src"),
    include_package_data=True,
    install_requires=requirements,
)
