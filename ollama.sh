#!/bin/bash

# Exit immediately if a command exits with a non-zero status (ensures stability)
set -e

# ==============================================================================
# SCRIPT TO START OLLAMA AND AGENT-ZERO PODMAN CONTAINER
#
# This script integrates best practices from Agent-Zero tutorials, including:
# 1. Automatic model pulling via Ollama.
# 2. Dynamic Podman network IP resolution (fixing host.docker.internal issues).
# 3. Validation checks for Ollama server binding.
# 4. Robust process/container cleanup.
# ==============================================================================

# --- Configuration Variables ---
OLLAMA_PORT=11434
AGENT0_HOST_PORT=50001
AGENT0_IMAGE="agent-zero-local:ready"
# Set your desired model here. This script will pull it if it's missing.
OLLAMA_MODEL_NAME="gpt-oss:20b" 

# Ensure persistent user data directory exists on host
mkdir -p "$(pwd)/usr" 

# 1. Dynamically determine the gateway IP of the Podman network
HOST_GATEWAY_IP=$(podman network inspect podman -f '{{(index .Subnets 0).Gateway}}' 2>/dev/null || echo "")

if [ -z "$HOST_GATEWAY_IP" ]; then
    echo "Warning: Could not dynamically determine Podman network gateway IP. Falling back to 'host.docker.internal'."
    OLLAMA_INTERNAL_URL="http://host.docker.internal:$OLLAMA_PORT"
    # Keep the original --add-host flag if fallback is necessary
    ADD_HOST_FLAG="--add-host host.docker.internal:host-gateway"
else
    # Use the discovered IP address directly (e.g., http://10.88.0.1:11434)
    OLLAMA_INTERNAL_URL="http://$HOST_GATEWAY_IP:$OLLAMA_PORT"
    echo "Using dynamically determined host IP for Ollama URL: $HOST_GATEWAY_IP"
    # Remove the problematic --add-host flag
    ADD_HOST_FLAG=""
fi


# --- 1. Cleanup and Prerequisite Checks ---
echo "--- 1. Stopping any existing Ollama servers and Agent-Zero containers..."

# Stop and remove any previously running agent0 containers forcefully
podman stop -t 5 agent0-ollama-runner attacker 2>/dev/null || true
podman rm -f agent0-ollama-runner attacker 2>/dev/null || true
echo "Previous agent0 containers removed."

# --- 1.5. Ensure the LLM model is pulled ---
echo -e "\n--- 1.5. Checking and pulling the required LLM model (${OLLAMA_MODEL_NAME}) ---"
if ! ollama list | grep -q "$OLLAMA_MODEL_NAME"; then
    echo "Model ${OLLAMA_MODEL_NAME} not found locally. Pulling now (this may take a few minutes)..."
    ollama pull "$OLLAMA_MODEL_NAME"
    if [ $? -ne 0 ]; then
        echo -e "\n❌ CRITICAL ERROR: Failed to pull model ${OLLAMA_MODEL_NAME}. Check your internet connection or Ollama installation."
        exit 1
    fi
else
    echo "Model ${OLLAMA_MODEL_NAME} is already available locally."
fi


# --- 2. Ensure Ollama Server is Listening ---
if lsof -i tcp:${OLLAMA_PORT} >/dev/null 2>&1; then
    echo "Ollama is already running and listening on port ${OLLAMA_PORT}."
else
    echo -e "\n--- 2. Starting Ollama server, binding to 0.0.0.0:${OLLAMA_PORT}..."
    export OLLAMA_HOST="0.0.0.0:$OLLAMA_PORT"
    ollama serve &
    sleep 3
fi


# --- 3. Run Agent-Zero Container ---
echo -e "\n--- 3. Starting Agent-Zero container (podman run)..."

# Build local patched image if not present
echo "Ensuring patched Agent Zero image is built..."
podman build -t "$AGENT0_IMAGE" .

podman run \
    --name agent0-ollama-runner \
    --detach \
    ${ADD_HOST_FLAG} \
    -p ${AGENT0_HOST_PORT}:80 \
    -v "$(pwd)/usr:/a0/usr:Z" \
    -e OLLAMA_API_BASE="$OLLAMA_INTERNAL_URL" \
    -e MODEL_NAME="$OLLAMA_MODEL_NAME" \
    -e CHAT_MODEL="$OLLAMA_MODEL_NAME" \
    $AGENT0_IMAGE

if [ $? -eq 0 ]; then
    echo -e "\n✅ Success! Agent-Zero container is running."
    echo "Agent-Zero is accessible at: http://localhost:${AGENT0_HOST_PORT}"
    echo "Ollama Base URL configured inside the container as: ${OLLAMA_INTERNAL_URL}"
    echo "Default model set to: ${OLLAMA_MODEL_NAME}"
    echo -e "\nTo see container logs and confirm Agent-Zero is connecting to Ollama:"
    echo "    podman logs -f agent0-ollama-runner"
else
    echo -e "\n❌ CRITICAL ERROR: Podman failed to start the container."
fi

# ==============================================================================
# --- FINAL INSTRUCTIONS ---
# To shut down the services cleanly:
# 1. Stop the container: podman stop agent0-ollama-runner
# 2. Kill the Ollama background process: kill $OLLAMA_PID
# ==============================================================================

# Important: Do not exit the script here. Keep the terminal open as the Ollama process is
# running in the background of this session.