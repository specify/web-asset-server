# VERSION          : 1
# DOCKER-VERSION   : 1.11
# TO_BUILD         : docker build --pull=true --no-cache --rm -t julienbreux/synology-gandi-dynamic-dns:latest .
# TO_SHIP          : docker push julienbreux/synology-gandi-dynamic-dns:latest
# TO_RUN           : docker run -ti --rm julienbreux/synology-gandi-dynamic-dns:latest
MAINTAINER Thierry Valero (IRD/MIVEGEC)

LABEL ird.mivegec.name='tvalero/web-asset-server'
LABEL ird.mivegec.description='Specify Web Asset Server in a container'
LABEL ird.mivegec.torun='docker run -it -d tvalero/web-asset-server:dev -v <Your data volume>:/home/specify/attachments:rw'


FROM python:2.7-onbuild

RUN apt-get update && apt-get install -y \
    imagemagick \
    ghostscript

ENV SPECIFY_KEY  None
ENV SPECIFY_HOST localhost

ENV SPECIFY_PORT 8080
EXPOSE 8080

ENV BASE_DIR /home/specify/attachments/
RUN mkdir -p /home/specify/attachments
VOLUME       /home/specify/attachments

ENTRYPOINT python server.py
