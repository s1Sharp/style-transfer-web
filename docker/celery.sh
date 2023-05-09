#!/bin/bash

cd src

if [[ "${1}" == "celery" ]]; then
  celery --app=task.tasks:celery worker -l INFO
elif [[ "${1}" == "flower" ]]; then
  celery --app=task.tasks:celery flower
fi
