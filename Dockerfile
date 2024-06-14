FROM ubuntu:20.04
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update \
    && apt-get --no-install-recommends -y install \
        tzdata \
        imagemagick \
        uwsgi \
        uwsgi-plugin-python3 \
        libimage-exiftool-perl \
    python3 \
    python3-pip
WORKDIR /tmp
COPY requirements.txt requirements.txt
COPY metadata_tools/requirements.txt /tmp/metadata_tools/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r /tmp/metadata_tools/requirements.txt
ENV TZ=America/Los_Angeles
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
WORKDIR /code
#CMD ["python3","./server.py"]