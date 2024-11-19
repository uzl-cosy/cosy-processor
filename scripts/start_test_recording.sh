#!/bin/bash

# Function to generate a random alphanumeric ID
generate_random_id() {
    cat /dev/urandom | tr -dc 'a-z0-9' | fold -w 10 | head -n 1
}

# Define the URL and any necessary curl options
URL="http://localhost:8000/recording/start"
CURL_OPTIONS="-X POST"

# Generate a random alphanumeric ID
RANDOM_ID=$(generate_random_id)

# Define the JSON body with the random ID
JSON_BODY=$(cat <<EOF
{
    "feedbackId": "$RANDOM_ID",
    "wordsToSay": ["Hello", "World"],
    "wordsNotToSay": ["Goodbye", "Universe"]
}
EOF
)

# Execute the curl command with JSON body
response=$(curl $CURL_OPTIONS -H "Content-Type: application/json" -d "$JSON_BODY" $URL)

# Display the result
echo "Response from server:"
echo "$response"