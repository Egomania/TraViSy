####### PYTHON LIBS ###################

# Flask imports
from flask import Flask
from flask import render_template
from flask import request
import flask

from werkzeug import secure_filename

#standard stuff
import os
import ConfigParser
import imp
import glob
from pydbus import SystemBus

#security stuff
import ssl

#threading stuff
from celery import Celery
from kombu import serialization

################# GLOABEL STUFF ########################

# Global vars

bus = SystemBus()
systemd = bus.get(".systemd1")
manager = systemd[".Manager"]

ConfigDefaults = {'SERVER_PEM': './cert/server.pem', 'SERVER_KEY': './cert/server.key', 'UPLOAD_FOLDER': './uploads', 'PORT':'443'}

Config = ConfigParser.ConfigParser(defaults=ConfigDefaults)
Config.read('./config/app.ini')

SERVER_PEM = Config.get('SecuritySetting', 'SERVER_PEM')
SERVER_KEY = Config.get('SecuritySetting', 'SERVER_KEY')

context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
context.load_cert_chain(SERVER_PEM, SERVER_KEY)

UPLOAD_FOLDER = Config.get('AppSetting', 'UPLOAD_FOLDER')
ALLOWED_EXTENSIONS = set(['pcap'])

PORT_USED = Config.getint('AppSetting', 'PORT')

REQUIRED_MODULES = [elem.strip() for elem in Config.get('AppSetting', 'SERVICES').split(',')]

# app setup

app = Flask(__name__)

modules = glob.glob("modules/*.py")
moduleNames = [ os.path.basename(f)[:-3] for f in modules if os.path.isfile(f) and 'init' not in f]

# load application imports
imports = []

for elem in moduleNames:
    my_module = imp.load_source(elem, './modules/' + elem + '.py')
    app.register_blueprint(my_module.module)
    newImport = [my_module.name, my_module.name, my_module.description]
    imports.append(newImport)

serialization.registry._decoders.pop("application/x-python-serialize")

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# do a very dirty hack and generate needed base.html file (insert module name and link)
with open("templates/baseGen.html", "r") as f:
    with open("templates/base.html", 'w') as newF:
        for line in f.readlines():
            if 'dirtyHackString' not in line:
                newF.write(line)
            else:
                for elem in imports:
                    newLine = '<a class="navbar-brand" href="/' + elem[1] + '">' + elem[0] + '</a> \n'
                    newF.write(newLine)

# check if required services are up

REQUIRED_MODULES_UNIT_NAMES = {}
for elem in REQUIRED_MODULES:
    REQUIRED_MODULES_UNIT_NAMES[elem] = None
    for unit in manager.ListUnits():
        if elem in unit[0]:
            unitName = unit[0]
            REQUIRED_MODULES_UNIT_NAMES[elem] = unitName
            if 'loaded' in unit[2] and 'active' in unit[3] and 'running' in unit[4]:
                print ('[OK] ' + unitName + ' running')
            else:
                print ('Start Service ' + unitName)
                systemd.StartUnit(unitName, 'fail')

# celery setup

def make_celery(app):
    celery = Celery("app", broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task
    class ContextTask(TaskBase):
        abstract = True
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery

app.config.update(
    CELERY_BROKER_URL='amqp://',
    CELERY_RESULT_BACKEND='rpc://',
    CELERY_ACCEPT_CONTENT=['application/json'],
    CELERY_TASK_SERIALIZER='json',
    CELERY_RESULT_SERIALIZER='json'
)

celery = make_celery(app)

# init functions

@app.before_first_request
def before_first_request():
    pass

############# WEBSITE RENDERING #############################

@app.route("/")
def index():
    return render_template("index.html", imps=imports)

@app.route("/backend")
def backend():
    return render_template("/backend/backend.html")

@app.route("/backend/serviceoverview")
def backend_serviceoverview():
    return render_template("/backend/serviceOverview.html")


########################################### MAIN ###########################################

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT_USED, debug=True, threaded=True, ssl_context=context)


    
