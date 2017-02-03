# TraViSy

## Installation

### System specific (apt-get install) - Ubuntu 15.10 Repo Version:

 * python >= 2.7.9
 * rabbitmq-server
 * mongodb
 * python-virtualenv
 * python-dev
 * python-libpcap
 * python-pip
 * libffi-dev
 * libxslt-dev
 * libxml2-dev
 * libz-dev
 * libcairo-dev
 * libpang1.0-dev
 * libpcap-dev

### Python-specific (pip install):

 * Flask
 * virtualenv
 * pymongo
 * dpkt
 * netifaces
 * bacpypes
 * celery
 * pylibpcap
 * Flask-WeasyPrint
 * pcapy

### Other preparation

#### Patch

dkpt: pcap.py
 * dpkt_remove_seek
to enable dpkt to read from pipes
 * Search via google to get patch 

#### Certificates

Place server certificates into /src/cert (.key and .pem)

#### Configuration File

Adapt configs if needed.

## Execution

 * service rabbitmq-server start
 * celery -A "app.celery" worker (sudo required)
 * python app.py

## Add own modules

Place .py file into /modules folder.
See test.py for minimal workin example.


