# pypi requirements
FROM python:3 as builder
RUN python3 -m pip install --upgrade pip setuptools wheel twine
RUN apt update && apt install -y vim


# python packages
FROM builder as stage
COPY requirements.txt .
RUN pip install -U -r requirements.txt


FROM stage as runner

LABEL maintainer="naisanza@gmail.com"
LABEL description="automonisaur core library"


WORKDIR /app

COPY automon automon
COPY README.md .
COPY LICENSE .
COPY entry.sh .
COPY unittests.sh .
COPY setup.py .


# run app
CMD ["/bin/bash"]

ENTRYPOINT ["/bin/bash", "entry.sh"]
