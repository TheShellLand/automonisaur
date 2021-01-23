import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="automonisaur", # Replace with your own username
    version="0.0.2",
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
    python_requires='>=3.6',
    install_requires=[
        'requests==2.22.0',
        'Flask==1.1.1',
        'Flask-Login==0.4.1',
        'Flask-WTF==0.14.2',
        'bcrypt==3.1.7',
        'elasticsearch==7.10.0',
        'neo4j-driver==1.7.4',
        'slackclient==2.2.1',
        'python-swiftclient==3.9.0',
        'python-keystoneclient==3.22.0',
        'splunk-sdk==1.6.13',
        'pytz==2020.1',
        'nest-asyncio==1.3.3',
        'xmltodict==0.12.0',
        'pytest==5.4.3',
        'coverage==5.2',
        'pytest-cov==2.10.0',
    ]
)
