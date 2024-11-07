# Base image
FROM ubuntu:24.04
ARG DEBIAN_FRONTEND=noninteractive

# Install system dependencies and Python packages
RUN apt-get update && apt-get install -y \
    ca-certificates tzdata wget curl python3-pip python3-setuptools \
    build-essential libffi-dev imagemagick libimage-exiftool-perl \
    gcc-aarch64-linux-gnu uwsgi uwsgi-plugin-python3 python3.12-venv\
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /tmp
# Create virtual environment in a different directory
RUN python3.12 -m venv venv
ENV PATH="/tmp/venv/bin:$PATH"
COPY requirements.txt /tmp/requirements.txt
COPY metadata_tools/requirements.txt /tmp/metadata_tools/requirements.txt
RUN /tmp/venv/bin/pip install --no-cache-dir -r /tmp/requirements.txt
RUN /tmp/venv/bin/pip install --no-cache-dir -r /tmp/metadata_tools/requirements.txt
ENV TZ=America/Los_Angeles
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
WORKDIR /code