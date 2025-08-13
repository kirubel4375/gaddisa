#!/bin/bash

# Get the directory of this script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd $DIR

# Activate Python environment if you're using virtualenv/venv on cPanel
# source ~/virtualenv/emergency_bot/bin/activate

# Kill any existing bot process
pkill -f "python run_cpanel_bot.py" || true

# Start bot in background, redirect output to logs
nohup python run_cpanel_bot.py > bot_output.log 2>&1 &

# Save the process ID for future reference
echo $! > bot.pid

# Print confirmation message
echo "Bot started with PID $(cat bot.pid)" 