FROM python:3

RUN python3 -m pip install -U opentelemetry-distro opentelemetry-exporter-otlp
RUN python3 -m pip install git+https://github.com/TheShellLand/opentelemetry-python-contrib.git@0.44b0#subdirectory=instrumentation/opentelemetry-instrumentation-aiohttp-server
RUN opentelemetry-bootstrap --action install
RUN python3 -m pip install -U opentelemetry-instrumentation-logging
