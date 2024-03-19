# OpenTelemetry

## Install Automatic Instrumentation

* https://opentelemetry.io/docs/languages/python/automatic/

```shell
python3 -m pip install -U opentelemetry-distro opentelemetry-exporter-otlp
python3 -m pip install git+https://github.com/TheShellLand/opentelemetry-python-contrib.git@0.44b0#subdirectory=instrumentation/opentelemetry-instrumentation-aiohttp-server
opentelemetry-bootstrap --action install

# python logging
python3 -m pip install -U opentelemetry-instrumentation-logging

# django
python3 -m pip install -U opentelemetry-instrumentation-django
```

## Known issues:

### Problem 1 (fixed):

fixed: https://github.com/open-telemetry/opentelemetry-python-contrib/issues/2053#issuecomment-1962248084

```
ERROR: No matching distribution found for opentelemetry-instrumentation-aiohttp-server==0.42b0 
```

reference: https://github.com/open-telemetry/opentelemetry-python-contrib/issues/2053

Solution:

* install using commit flag

> I have added a new tag: 0.43b0hotfix. This can be used to install
> opentelemetry-instrumentation-aiohttp-server and
> opentelemetry-resource-detector-container with the following pip commands:

opentelemetry-instrumentation-aiohttp-server:

```shell
python3 -m pip install git+https://github.com/open-telemetry/opentelemetry-python-contrib.git@v0.44b0#subdirectory=instrumentation/opentelemetry-instrumentation-aiohttp-server
```

opentelemetry-resource-detector-container:

```shell
python3 -m pip install git+https://github.com/open-telemetry/opentelemetry-python-contrib.git@v0.44b0#subdirectory=resource/opentelemetry-resource-detector-container
```

solution: https://github.com/open-telemetry/opentelemetry-python-contrib/issues/2053#issuecomment-1928485674
