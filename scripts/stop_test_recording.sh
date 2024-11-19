#!/bin/bash

# Define the URL and any necessary curl options
URL="http://localhost:8000/recording/stop"
CURL_OPTIONS="-X POST"

# Execute the curl command with JSON body
response=$(curl $CURL_OPTIONS $URL)

# Display the result
echo "Response from server:"
echo "$response"