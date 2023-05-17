#!/bin/bash

alembic upgrade head
cd src
uvicorn main:app --workers 1 --reload
