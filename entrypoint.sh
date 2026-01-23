#!/bin/bash

# Ensure dirs
mkdir -p /app/__DISAVOW_DATA__/INGEST /app/__DISAVOW_DATA__/OUTPUT /app/conf
chown -R disavow:disavow /app/__DISAVOW_DATA__ /app/conf

# Run the bro
exec gosu disavow python app.py
