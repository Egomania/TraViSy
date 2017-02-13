#threading stuff
import celery


from flask import Blueprint
from flask import render_template

name = 'test'
description = 'test module'

module = Blueprint(name, __name__, template_folder='templates')
celery = celery.Celery('tasks', backend='rpc://', broker='amqp://')

@module.route('/' + name)
def test():
    return render_template("test/index.html")
