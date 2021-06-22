#! /bin/bash
gunicorn big_screen.wsgi -c ../../conf/gunicorn123.py &