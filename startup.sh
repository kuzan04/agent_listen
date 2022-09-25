#!/bin/bash
PATH="$( cd -- "$(dirname "$0")" > /dev/null 2>&1 ; pwd -P )"
#source $PATH/env/bin/activate
/usr/bin/python3 $PATH/server.py
#$(/usr/local/bin/pm2 start $PATH/server.py --name agentListen --interpretor python3)
