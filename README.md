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
[![master](https://github.com/TheShellLand/automonisaur/actions/workflows/python39.yml/badge.svg)](https://github.com/TheShellLand/automonisaur/actions/workflows/python39.yml)
[![master](https://github.com/TheShellLand/automonisaur/actions/workflows/python38.yml/badge.svg)](https://github.com/TheShellLand/automonisaur/actions/workflows/python38.yml)
[![master](https://github.com/TheShellLand/automonisaur/actions/workflows/python37.yml/badge.svg)](https://github.com/TheShellLand/automonisaur/actions/workflows/python37.yml)
[![master](https://github.com/TheShellLand/automonisaur/actions/workflows/python36.yml/badge.svg)](https://github.com/TheShellLand/automonisaur/actions/workflows/python36.yml)

[![Downloads](https://pepy.tech/badge/automonisaur)](https://pepy.tech/project/automonisaur)
[![Downloads](https://pepy.tech/badge/automonisaur/month)](https://pepy.tech/project/automonisaur)
[![Downloads](https://pepy.tech/badge/automonisaur/week)](https://pepy.tech/project/automonisaur)

[//]: # ([![codecov]&#40;https://codecov.io/gh/TheShellLand/automonisaur/branch/master/graph/badge.svg&#41;]&#40;https://codecov.io/gh/TheShellLand/automonisaur&#41;)

### About

This library adds some easier-to-use wrappers around common services for data science and threat intelligence.

Provides easier clients and configuration options, as well as any additional helpers to get things up and running.

Github issues and feature requests welcomed.

### Integrations

- airport
- elasticsearch
- flask
- google people api
- logging
- minio
- neo4j
- nmap
- requests
- selenium
- sentryio
- slack
- snmp
- splunk
- swift

#### Requires

- python >= 3.7

_Note: install requirements.txt to use all integrations_

#### install core library

```shell script
/bin/bash install.sh
```

#### install integration libraries

```shell script
# shell script
/bin/bash requirements.sh

# pip
python3 -m pip install -U -r requirements.txt

# pip 
python3 -m pip install -U -r https://raw.githubusercontent.com/TheShellLand/automonisaur/master/requirements.txt
```

#### unittest locally

```shell script
/bin/bash unittests.sh
```
