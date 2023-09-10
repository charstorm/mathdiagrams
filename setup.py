from setuptools import setup

requirements = []

with open("requirements.txt") as file:
    requirements = [line.strip() for line in file]

setup(
    name="mathdiagrams",
    version="0.1dev",
    description="A python library to create a simple proof diagrams",
    author="Vinay Krishnan",
    author_email="nk.vinay@zohomail.in",
    url="https://github.com/charstorm/mathdiagrams/",
    packages=["mathdiagrams"],
    python_requires=">=3.11",
    install_requires=requirements,
)
