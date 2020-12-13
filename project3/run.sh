#!/bin/bash
  
if [[ $HOSTNAME == *"attu"* ]]; then
        echo "running attu config, using compiled"
        chmod 755 p3
        ./p3 $1
else
        echo "running local config, assuming proper packets installed per directions"
        pip install -r requirements.txt
	python3 p3.py $1

fi

