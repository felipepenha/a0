#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Stop and remove existing containers and network to ensure a clean start
podman stop vulnerable_container attacker >/dev/null 2>&1 || true
podman rm vulnerable_container attacker >/dev/null 2>&1 || true
podman network rm -f sec_test_net >/dev/null 2>&1 || true

# Create a network for the containers
podman network create --driver bridge sec_test_net

# Run the target container
echo "Starting target container (OWASP Juice Shop)..."
podman pull bkimminich/juice-shop
podman run -d --name vulnerable_container --net sec_test_net -p 8080:3000 bkimminich/juice-shop

# Ensure persistent user data directory exists on host
mkdir -p "$(pwd)/usr"
mkdir -p "$(pwd)/logs"

# Run the agent0 container (using patched image with persistent volume)
echo "Building patched Agent Zero image..."
podman build -t agent-zero-local:ready .

echo "Starting Agent Zero container..."
podman run -d --name attacker --net sec_test_net -p 50001:80 -v "$(pwd)/usr:/a0/usr:Z" agent-zero-local:ready

echo "Waiting for Agent Zero container services to initialize..."
sleep 10

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="$(pwd)/logs/agent_session_${TIMESTAMP}.log"
LATEST_LOG="$(pwd)/logs/latest.log"

echo ""
echo "--------------------------------------------------------"
echo "✅ Agent Zero Container is up and running!"
echo "--------------------------------------------------------"
echo "Target App (Juice Shop): http://localhost:8080"
echo "Agent Zero Web UI:       http://localhost:50001"
echo "Log File Output:        $LOG_FILE"
echo "--------------------------------------------------------"
echo ""

PROMPT="Inspect the main HTTP response headers and public configuration files (such as robots.txt and sitemap.xml) at http://vulnerable_container:3000. Check for the presence of standard security headers (like Content-Security-Policy, X-Frame-Options, and Strict-Transport-Security) and summarize the findings passively."

echo "Sending prompt to Agent Zero session via API client (send_agent_prompt.py)..."
python3 send_agent_prompt.py "$PROMPT" "http://localhost:50001" 2>&1 | tee "$LOG_FILE" | tee "$LATEST_LOG"

