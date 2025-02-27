#!/bin/bash

URL="flask-api.local:5000/api/v1/strings/random"

# Run infinite loop of requests until stopped
echo "Generating load - press Ctrl+C to stop"
while true; do
  for i in {1..20}; do
    xh get $URL &> /dev/null &
  done
  sleep 0.5
done
