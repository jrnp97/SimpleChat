#!/usr/bin/env bash

WORK_DIR=/src

cd $WORK_DIR || exit

if python manage.py test; then
  echo 'Test Passed!!'
else
	echo 'Tests Failed'
	exit 1
fi

if python manage.py migrate --no-input; then
  echo 'Migrations executed!!'
else
	echo 'Error migration'
	exit 1
fi

python manage.py runserver 0.0.0.0:8000
