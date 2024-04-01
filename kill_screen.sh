#!/bin/bash

# Sometimes you end up with more than one instance of screen running and it 
# screws up everything as the incoming bytes go to random instances and none
# get the full picture. This gets you back to a sane state by KILLing them all.

# Define the command to search for
command_to_kill="SCREEN /dev/ttyUSB0 115200"

# Get the process IDs (PIDs) of the matching processes
pids=$(ps aux | grep "$command_to_kill" | grep -v grep | awk '{print $2}')

# Check if any processes were found
if [ -n "$pids" ]; then
    # Kill each process found
    echo "Killing processes:"
    echo "$pids"
    kill $pids
else
    echo "No matching processes found."
fi
