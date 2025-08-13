#!/bin/bash

# Get the directory of this script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd $DIR

# Check if PID file exists
if [ -f "bot.pid" ]; then
    PID=$(cat bot.pid)
    echo "Stopping bot process with PID: $PID"
    
    # Kill the process
    kill $PID 2>/dev/null || pkill -f "python run_cpanel_bot.py"
    
    # Remove the PID file
    rm bot.pid
    
    echo "Bot stopped successfully"
else
    echo "No bot PID file found, trying to find and kill the process..."
    pkill -f "python run_cpanel_bot.py" && echo "Bot stopped successfully" || echo "No running bot process found"
fi 