FROM ubuntu:20.04
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get --no-install-recommends install -y \
        software-properties-common \
        python-setuptools \
        tzdata \
        wget \
        curl \
        build-essential \
        libssl-dev \
        libbz2-dev \
        libreadline-dev \
        libsqlite3-dev \
        libffi-dev \
        zlib1g-dev \
        libgdbm-dev \
        liblzma-dev \
        imagemagick \
        uwsgi \
        uwsgi-plugin-python3 \
        libimage-exiftool-perl \
        gcc-aarch64-linux-gnu \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python 3.12
RUN apt-get update && \
    apt-get install -y software-properties-common wget && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y python3.12 python3.12-venv python3.12-dev python3.12-distutils && \
    rm -rf /var/lib/apt/lists/*


RUN wget https://bootstrap.pypa.io/get-pip.py && \
    python3.12 get-pip.py && \
    rm get-pip.py

# Set Python 3.12 as the default python3
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.12 1

RUN python3 --version

#install pip under 3.12
RUN python3.12 -m pip install --upgrade pip setuptools wheel

RUN python3.12 -m pip install uwsgi

# Install Python packages
WORKDIR /tmp
COPY requirements.txt requirements.txt
COPY metadata_tools/requirements.txt /tmp/metadata_tools/requirements.txt
RUN python3.12 -m pip install --no-cache-dir -r requirements.txt
RUN python3.12 -m pip install --no-cache-dir -r metadata_tools/requirements.txt
ENV TZ=America/Los_Angeles
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
WORKDIR /code
# CMD ["python","./server.py"]
