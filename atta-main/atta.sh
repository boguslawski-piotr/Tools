#!/bin/bash

# Resolve the location of the Atta installation.
# This includes resolving any symlinks.
PRG=$0
while [ -h "$PRG" ]; do
  ls=`ls -ld "$PRG"`
  link=`expr "$ls" : '^.*-> \(.*\)$' 2>/dev/null`
  if expr "$link" : '^/' 2> /dev/null >/dev/null; then
    PRG="$link"
  else
    PRG="`dirname "$PRG"`/$link"
  fi
done
ATTA_HOME=`dirname "$PRG"`

# Absolutize dir.
oldpwd=`pwd`
cd "${ATTA_HOME}"
ATTA_HOME=`pwd`
cd "${oldpwd}"
unset oldpwd

# Run Atta.
python $ATTA_HOME/main.py $@
