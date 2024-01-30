# OpenTelemetry

## Install Automatic Instrumentation

* https://opentelemetry.io/docs/languages/python/automatic/

```shell
python3 -m pip install -U opentelemetry-distro opentelemetry-exporter-otlp
opentelemetry-bootstrap --action install

python3 -m pip install -U opentelemetry-instrumentation-logging
```

## Known issues:

### Problem 1:
```
ERROR: No matching distribution found for opentelemetry-instrumentation-aiohttp-server==0.42b0 
```

https://github.com/open-telemetry/opentelemetry-python-contrib/issues/2053

Solution:

* install using github

```shell
python3 -m pip install git+https://github.com/open-telemetry/opentelemetry-python-contrib#subdirectory=opentelemetry-instrumentation-aiohttp-server
```
