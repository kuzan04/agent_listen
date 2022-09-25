#!/bin/bash
PATH="$( cd -- "$(dirname "$0")" > /dev/null 2>&1 ; pwd -P )"
`source $PATH/env/bin/activate`
#`sudo python3 $PATH/server.py`
`pm2 start $PATH/server.py --name agentListen --interpretor python3`
