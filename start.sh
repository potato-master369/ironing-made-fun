#!/bin/bash

gunicorn --config gunicorn_config.py app:app --error-logfile gunicorn-error.log
