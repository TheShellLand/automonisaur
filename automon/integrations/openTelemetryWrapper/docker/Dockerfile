FROM python:3

RUN python3 -m pip install -U opentelemetry-distro opentelemetry-exporter-otlp
RUN opentelemetry-bootstrap --action install

RUN python3 -m pip install -U opentelemetry-instrumentation-logging
