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

Place server certificate and key into ```/src/cert``` (.key and .pem).

```openssl req -newkey rsa:2048 -new -nodes -x509 -days 3650 -keyout server.key -out server.pem```

#### Configuration File

Adapt configs if needed.
See ```src/config/``` Folder, configuration of overall app is done in app.ini, configuration of modules is done in seperate .ini-files.

## Execution

 * ```service rabbitmq-server start```
 * ```celery -A "app.celery" worker (sudo required)```
 * ```python2 app.py```

## Add own modules

Place .py file into ```/modules``` folder.
See ```test.py``` for minimal working example.


