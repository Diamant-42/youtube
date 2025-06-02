#!/bin/bash

ulimit -n 65535  # Augmente la limite de fichiers ouverts
SCRIPT="crawler.py"
LOGFILE="watchdog.log"

echo "🚀 Watchdog lancé pour $SCRIPT"
echo "[`date`] Watchdog started" >> "$LOGFILE"

while true; do
    echo "[`date`] Lancement de $SCRIPT" | tee -a "$LOGFILE"
    python3 "$SCRIPT"
    
    echo "[`date`] Crash détecté, redémarrage" | tee -a "$LOGFILE"
done