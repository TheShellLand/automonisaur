FROM python:3

LABEL maintainer="naisanza@gmail.com"
LABEL description="automon core library"

WORKDIR /app

COPY automon automon
COPY entry.sh .
COPY unittests.sh .
COPY requirements.txt .
COPY setup.py .

RUN pip install -r requirements.txt

# run app
CMD ["/bin/bash"]

ENTRYPOINT ["/bin/bash", "entry.sh"]
