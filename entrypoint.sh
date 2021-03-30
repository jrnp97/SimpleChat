#!/usr/bin/env bash

WORK_DIR=/src

if python $WORK_DIR/manage.py test; then
  echo 'Test Passed!!'
else
	echo 'Tests Failed'
	exit 1
fi

if python $WORK_DIR/manage.py migrate --no-input; then
  echo 'Migrations executed!!'
else
	echo 'Error migration'
	exit 1
fi

python $WORK_DIR/manage.py runserver 0.0.0.0:8000
