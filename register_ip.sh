#!/bin/bash
#
# Register EC2 instance public IP with DNS subdomain service
#
# Usage:
#   ./register_ip.sh
#
# The script will:
#   1. Load values from .env file if present
#   2. Prompt for any missing values (username, label, token)
#
# To use a .env file, create a file named .env in the same directory
# with the following format:
#   USERNAME=yourusername
#   LABEL=web
#   TOKEN=your-bearer-token-here
#
# Security: Never commit .env files to version control!

API_URL="https://webapps.cs.moravian.edu/awsdns/"

# Load .env file if it exists
if [ -f .env ]; then
    source .env
fi

# Prompt for values if not set (from .env or otherwise)
if [ -z "$USERNAME" ]; then
    read -p "Enter your username: " USERNAME
fi

if [ -z "$LABEL" ]; then
    read -p "Enter subdomain label (e.g., 'web', 'app', 'db'): " LABEL
fi

if [ -z "$TOKEN" ]; then
    read -p "Enter your bearer token: " TOKEN
fi

# Validate inputs
if [ -z "$USERNAME" ] || [ -z "$TOKEN" ] || [ -z "$LABEL" ]; then
    echo "ERROR: Username, token, and label are all required" >&2
    exit 1
fi

# Get public IP
echo "Retrieving public IP address..."
PUBLIC_IP=$(curl -s --max-time 5 http://checkip.amazonaws.com)

if [ -z "$PUBLIC_IP" ]; then
    echo "ERROR: Could not determine public IP address" >&2
    exit 1
fi

echo "Public IP: $PUBLIC_IP"
echo "Registering subdomain: ${USERNAME}${LABEL}..."

# Make API call
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$API_URL/setip" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"name\":\"$USERNAME\",\"label\":\"$LABEL\",\"ipAddress\":\"$PUBLIC_IP\"}")

# Extract HTTP status code (last line)
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
# Extract response body (all but last line)
BODY=$(echo "$RESPONSE" | sed '$d')

# Check result
if [ "$HTTP_CODE" -eq 200 ]; then
    echo "SUCCESS: Subdomain ${USERNAME}${LABEL} registered with IP $PUBLIC_IP"
    exit 0
else
    echo "ERROR: Registration failed (HTTP $HTTP_CODE)" >&2
    if [ -n "$BODY" ]; then
        echo "$BODY" | python3 -m json.tool 2>/dev/null || echo "$BODY"
    fi
    exit 1
fi

