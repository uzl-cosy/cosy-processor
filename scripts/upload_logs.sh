#!/bin/bash

# Define the directory containing the log files
LOG_DIR="/Users/finnstoldt/Projects/laboratorium-cosy-v2/logs"

# Define the API URL and device ID
API_URL="https://cosy.uni-luebeck.de:3011/log"
DEVICE_ID="cosyX"

# Get today's date in yyyy-MM-dd format
TODAY=$(date +"%Y-%m-%d")

# Create a temporary file
TEMP_FILE=$(mktemp /tmp/logfile.XXXXXX)

# Define yellow color and reset color
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Prompt user for incident report in German with ASCII decoration and yellow color
echo -e "${YELLOW}*******************************"
echo -e "*       VORFALLBERICHT       *"
echo -e "*******************************"
echo -e "*                             *"
echo -e "* Bitte geben Sie den         *"
echo -e "* Vorfallbericht ein          *"
echo -e "* (beenden mit EOF durch      *"
echo -e "* Drücken von Ctrl+D):        *"
echo -e "*                             *"
echo -e "*******************************${NC}"

# Read multi-line incident report
INCIDENT_REPORT=$(cat)

# Create an ASCII box with the incident report
ASCII_BOX=$(printf "***************************\n*       VORFALLBERICHT       *\n***************************\n$INCIDENT_REPORT\n***************************\n")

# Write the ASCII box to the temporary file
echo -e "$ASCII_BOX" > "$TEMP_FILE"

# Append content of all log files starting with today's date to the temporary file
for file in "$LOG_DIR/$TODAY"*; do
  if [[ -f $file ]]; then
    cat "$file" >> "$TEMP_FILE"
  fi
done

# Send the temporary file to the API and suppress the output if successful
curl -F "file=@$TEMP_FILE" "$API_URL?deviceId=$DEVICE_ID" > /dev/null 2>&1

# Clean up the temporary file
rm "$TEMP_FILE"

echo "Log file sent to API."