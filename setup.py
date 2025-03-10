import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="automonisaur",
    version="0.6.17",
    author="naisanza",
    author_email="naisanza@gmail.com",
    description="Core libraries for automonisaur",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/TheShellLand/automonisaur",
    packages=setuptools.find_packages(),
    tests_require=["pytest"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    ],
    license_files="LICENSE",
    python_requires='>=3.10',
    install_requires=[]
)
