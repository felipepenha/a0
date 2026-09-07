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

# --- Ollama Setup & Configuration ---
OLLAMA_PORT=11434
OLLAMA_MODEL_NAME="gpt-oss:20b"

# Dynamically determine the gateway IP of the Podman network
HOST_GATEWAY_IP=$(podman network inspect podman -f '{{(index .Subnets 0).Gateway}}' 2>/dev/null || echo "")

if [ -z "$HOST_GATEWAY_IP" ]; then
    echo "Warning: Could not determine Podman gateway IP. Falling back to host.docker.internal."
    OLLAMA_INTERNAL_URL="http://host.docker.internal:$OLLAMA_PORT"
    ADD_HOST_FLAG="--add-host host.docker.internal:host-gateway"
else
    OLLAMA_INTERNAL_URL="http://$HOST_GATEWAY_IP:$OLLAMA_PORT"
    ADD_HOST_FLAG=""
fi

# Ensure required Ollama model is available
if ! ollama list 2>/dev/null | grep -q "$OLLAMA_MODEL_NAME"; then
    echo "Pulling required Ollama model ($OLLAMA_MODEL_NAME)..."
    ollama pull "$OLLAMA_MODEL_NAME" || true
fi

# Start background Ollama server if not already running
if ! lsof -i tcp:${OLLAMA_PORT} >/dev/null 2>&1; then
    echo "Starting local Ollama server on 0.0.0.0:${OLLAMA_PORT}..."
    export OLLAMA_HOST="0.0.0.0:$OLLAMA_PORT"
    ollama serve &
    sleep 3
fi

# Run the agent0 container (configured to use local Ollama instance)
echo "Building patched Agent Zero image..."
podman build -t agent-zero-local:ready .

echo "Starting Agent Zero container (configured for local Ollama)..."
podman run -d \
    --name attacker \
    --net sec_test_net \
    ${ADD_HOST_FLAG} \
    -p 50001:80 \
    -v "$(pwd)/usr:/a0/usr:Z" \
    -e OLLAMA_API_BASE="$OLLAMA_INTERNAL_URL" \
    -e MODEL_NAME="$OLLAMA_MODEL_NAME" \
    -e CHAT_MODEL="$OLLAMA_MODEL_NAME" \
    agent-zero-local:ready

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

echo "Sending prompt to Agent Zero session via API client (prompt.py)..."
python3 prompt.py "$PROMPT" "http://localhost:50001" 2>&1 | tee "$LOG_FILE" | tee "$LATEST_LOG"

