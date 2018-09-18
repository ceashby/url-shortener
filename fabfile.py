import json

from fabric.decorators import task
from fabric.operations import local


@task
def dev_server():
    start_redis()
    local('FLASK_APP=url_shortener/wsgi.py python -m flask run --with-threads')


@task
def test():
    local('python -m unittest discover')


@task
def start_redis():
    local('redis-server &')


def stop_redis():
    local('redis-cli shutdown')


