import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="automonisaur",
    version="0.0.22",
    author="naisanza",
    author_email="naisanza@gmail.com",
    description="Core libraries for automonisaur",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/TheShellLand/automon-core",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
    install_requires=[
        'Flask-Login>=0.5.0',
        'Flask-WTF>=0.14.3',
        'Flask>=1.1.2',
        'bcrypt>3.1.7',
        'coverage>=5.4',
        'elasticsearch>=7.11.0',
        'neo4j-driver>=4.2.1',
        'nest-asyncio>=1.5.1',
        'pytest-cov>=2.11.1',
        'pytest>=6.2.2',
        'python-keystoneclient>=4.2.0',
        'python-swiftclient>=3.11.0',
        'pytz>=2021.1',
        'requests>=2.25.1',
        'slackclient>=2.9.3',
        'splunk-sdk>=1.6.15',
        'xmltodict>=0.12.0'
    ]
)
