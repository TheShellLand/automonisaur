# pypi requirements
FROM python:3.11 AS builder
RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install --upgrade setuptools
RUN python3 -m pip install --upgrade wheel
RUN python3 -m pip install --upgrade twine
RUN apt update && apt install -y vim
COPY requirements.txt .
RUN pip install -U -r requirements.txt


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