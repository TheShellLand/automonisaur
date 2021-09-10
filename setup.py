import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="automonisaur",
    version="0.0.32",
    author="naisanza",
    author_email="naisanza@gmail.com",
    description="Core libraries for automonisaur",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/TheShellLand/automonisaur",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        'Flask-Login>=0.5.0',
        'Flask-WTF>=0.15.1',
        'Flask>=2.0.1',
        'bcrypt>3.1.7',
        'coverage>=5.4',
        'elasticsearch>=7.14.0',
        'jupyterlab>=3.1.9',
        'minio>=7.1.0',
        'neo4j-driver>=4.3.4',
        'nest-asyncio>=1.5.1',
        'numpy>=1.21.2',
        'pandas>=1.3.2',
        'psutil>=5.8.0',
        'pytest-cov>=2.12.1',
        'pytest>=6.2.4',
        'python-keystoneclient>=4.2.0',
        'python-swiftclient>=3.12.0',
        'pytz>=2021.1',
        'requests>=2.26.0',
        'selenium>=3.141.0',
        'slackclient>=2.9.3',
        'splunk-sdk>=1.6.16',
        'urllib3>=1.26.6',
        'xmltodict>=0.12.0'
    ]
)
