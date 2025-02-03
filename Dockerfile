# pypi requirements
FROM python:3.11 AS builder
RUN python3 -m pip install --upgrade --break-system-packages --no-cache-dir pip && \
    python3 -m pip install --upgrade --break-system-packages --no-cache-dir setuptools && \
    python3 -m pip install --upgrade --break-system-packages --no-cache-dir wheel && \
    python3 -m pip install --upgrade --break-system-packages --no-cache-dir twine && \
    apt update && apt install -y vim && \
    apt clean && \
    rm -rf /var/cache/apt/archives /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade --break-system-packages --no-cache-dir -r requirements.txt


FROM builder AS runner
LABEL maintainer="naisanza@gmail.com"
LABEL description="automonisaur core library"

WORKDIR /automonisaur

COPY automon automon
COPY README.md .
COPY LICENSE .
COPY docker/entry.sh .
COPY unittests.sh .
COPY setup.py .

CMD ["/bin/bash"]
ENTRYPOINT ["/bin/bash", "entry.sh"]
