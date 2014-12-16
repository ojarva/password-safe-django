#!/bin/sh
#
# Add this file to crontab to start Vimma at boot:
# @reboot /home/vimma/vimma/bin/vimma.sh

PROJDIR=$HOME/passwordsafe
OUTLOG="$PROJDIR/logs/access.log"
ERRLOG="$PROJDIR/logs/error.log"
PIDFILE="$PROJDIR/passwordsafe.pid"
SOCKET="$PROJDIR/passwordsafe.sock"

cd $PROJDIR
if [ -f $PIDFILE ]; then
    kill `cat -- $PIDFILE`
    rm -f -- $PIDFILE
fi

/usr/bin/env - \
  PYTHONPATH="../python:.." \
  ./manage.py runfcgi --settings=passwordsafe.settings socket=$SOCKET pidfile=$PIDFILE workdir=$PROJDIR outlog=$OUTLOG errlog=$ERRLOG

chmod a+w $SOCKET
