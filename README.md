![](https://github.com/TheShellLand/automonisaur/raw/master/docs/images/sauruspark.gif)

# Automonisaur: Core Libraries

**[about](#about)** |
**[integrations](#integrations)** |
**[install](#install)** |
**[docker](docker)** |
**[unittest locally](#unittest-locally)** |
**[codecov](https://codecov.io/gh/TheShellLand/automonisaur)** |
**[pypi](https://pypi.org/project/automonisaur/)**

[![master](https://github.com/TheShellLand/automonisaur/actions/workflows/ci.yml/badge.svg)](https://github.com/TheShellLand/automonisaur/actions/workflows/ci.yml)
[![master](https://github.com/TheShellLand/automonisaur/actions/workflows/python312.yml/badge.svg)](https://github.com/TheShellLand/automonisaur/actions/workflows/python312.yml)
[![master](https://github.com/TheShellLand/automonisaur/actions/workflows/python311.yml/badge.svg)](https://github.com/TheShellLand/automonisaur/actions/workflows/python311.yml)
[![master](https://github.com/TheShellLand/automonisaur/actions/workflows/python310.yml/badge.svg)](https://github.com/TheShellLand/automonisaur/actions/workflows/python310.yml)
[![master](https://github.com/TheShellLand/automonisaur/actions/workflows/python39.yml/badge.svg)](https://github.com/TheShellLand/automonisaur/actions/workflows/python39.yml)
[![master](https://github.com/TheShellLand/automonisaur/actions/workflows/python38.yml/badge.svg)](https://github.com/TheShellLand/automonisaur/actions/workflows/python38.yml)
[![master](https://github.com/TheShellLand/automonisaur/actions/workflows/python37.yml/badge.svg)](https://github.com/TheShellLand/automonisaur/actions/workflows/python37.yml)

[![Downloads](https://static.pepy.tech/badge/automonisaur)](https://pepy.tech/project/automonisaur)
[![Downloads](https://static.pepy.tech/badge/automonisaur/month)](https://pepy.tech/project/automonisaur)
[![Downloads](https://static.pepy.tech/badge/automonisaur/week)](https://pepy.tech/project/automonisaur)

[//]: # ([![codecov]&#40;https://codecov.io/gh/TheShellLand/automonisaur/branch/master/graph/badge.svg&#41;]&#40;https://codecov.io/gh/TheShellLand/automonisaur&#41;)

### About

This library adds some easier-to-use wrappers around common services for data science and threat intelligence.

Provides easier clients and configuration options, as well as any additional helpers to get things up and running.

Github issues and feature requests welcomed.

### Integrations

- airport
- beautifulsoup
- elasticsearch
- facebook groups
- flask
- google auth api
- google people api
- google sheets api
- instagram
- logging
- minio
- neo4j
- nmap
- requests
- scrapy
- selenium
- sentryio
- slack
- snmp
- splunk
- swift

#### Requires

- python >= 3.8

_Note: install requirements.txt to use all integrations_

#### install core library

```shell script
/bin/bash install.sh
```

#### install integration libraries

```shell script
# shell script
/bin/bash install-requirements.sh

# pip
python3 -m pip install -U -r requirements.txt

# pip 
python3 -m pip install -U -r https://raw.githubusercontent.com/TheShellLand/automonisaur/master/requirements.txt
```

#### unittest locally

```shell script
/bin/bash unittests.sh
```
