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
