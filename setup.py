import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="automonisaur",
    version="0.2.23",
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
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
    install_requires=[]
)
