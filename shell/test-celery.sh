#! /bin/bash
python manage.py celery worker -P eventlet -c 10 --loglevel=info &