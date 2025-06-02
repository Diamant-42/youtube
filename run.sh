#!/bin/bash
echo "🚀 Lancement du crawler + keep-alive..."
source .env

# lance le crawler
./watchdog.sh &

# lance le keep-alive
python keepalive.py &
