#!/bin/bash

# used to save the gpid.
PID_FILE=discern.pid 

case "$1" in 
	start) 
		# fire up the discern server 
		python manage.py runserver 127.0.0.1:7999 --nostatic --settings=discern.settings --pythonpath=. &
		# launch the message queue via celeryd 
		python manage.py celeryd -B --settings=discern.settings --pythonpath=.  --loglevel=debug --logfile=/tmp/celery$$.out &
		echo "-$$" > ${PID_FILE}
		;;
	stop) 
		cat ${PID_FILE}  | xargs kill -TERM
		rm ${PID_FILE} 
		;;
	*)
		echo "Usage: $0 (start|stop)"
		exit 1
esac

exit 0
