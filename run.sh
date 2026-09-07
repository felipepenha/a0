#!/bin/bash

# # Working Version (Dec 2025)
# podman run -d \
#   --name agent-zero-v0-9-7 \
#   -p 8080:80 \
#   --restart unless-stopped \
#   agent0ai/agent-zero:v0.9.7

# # Working Version
# podman run -d \
#   --name agent-zero-v1-9 \
#   -p 8080:80 \
#   --restart unless-stopped \
#   agent0ai/agent-zero:v1.9

# # NOT WORKING !!
# podman run -d \
#   --name agent-zero-v1-10 \
#   -p 8080:80 \
#   --restart unless-stopped \
#   agent0ai/agent-zero:v1.10

# Ensure persistent user data directory exists on host
mkdir -p "$(pwd)/usr"

# Build the patched local image if not already built (or to update it)
echo "Building patched Agent Zero image (downgrading cryptography to prevent SIGILL)..."
podman build --no-cache -t agent-zero-local:ready .

# Stop and clean up any existing container by the same name
echo "Cleaning up existing container..."
podman stop agent-zero-local 2>/dev/null
podman rm agent-zero-local 2>/dev/null

# Run the patched local container with persistent host volume mount for user data
echo "Starting patched Agent Zero container..."
podman run -d \
  --name agent-zero-local \
  -p 8080:80 \
  -v "$(pwd)/usr:/a0/usr:Z" \
  --restart unless-stopped \
  agent-zero-local:ready

echo ""
echo "---------------------"
echo -e "http://localhost:8080"
echo "---------------------"
echo ""