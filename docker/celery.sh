#!/bin/bash

cd src

if [[ "${1}" == "celery" ]]; then
  celery --app=task.tasks:celery worker --pool=threads --concurrency=1 -l INFO
elif [[ "${1}" == "flower" ]]; then
  celery --app=task.tasks:celery flower
fi
