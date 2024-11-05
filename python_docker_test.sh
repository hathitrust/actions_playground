#!/bin/bash

# Test if the server responds on port 7000
URL="http://localhost:7000/index.html"
TRIES=10
INTERVAL=5
for (( i=1; i<=TRIES; i++)); do
    #Check status codes
    STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$URL")
        if [ "$STATUS" -eq 200 ]; then
            echo "Success"
            exit 0
        elif [ "$STATUS" -eq 404 ]; then
            echo " Attepnt $i - Endpoint returned a status of 404. Retrying in $INTERVAL seconds."
            sleep $INTERVAL
        else
            echo "Unexpected status of $STATUS"
            exit 1
        fi
    done