#!/bin/bash

# Stop and remove existing containers and network to ensure a clean start
podman stop vulnerable_container attacker >/dev/null 2>&1
podman rm vulnerable_container attacker >/dev/null 2>&1
podman network rm sec_test_net >/dev/null 2>&1

# Create a network for the containers
podman network create --driver bridge sec_test_net

# Run the vulnerable container
echo "Starting vulnerable container..."
podman pull bkimminich/juice-shop
podman run -d --name vulnerable_container --net sec_test_net -p 8080:3000 bkimminich/juice-shop

# Ensure persistent user data directory exists on host
mkdir -p "$(pwd)/usr"

# Run the agent0 container for attacking (using patched image with persistent volume)
echo "Building patched Agent Zero image..."
podman build -t agent-zero-local:ready .

echo "Starting agent0 container..."
podman run -d --name attacker --net sec_test_net -p 50001:80 -v "$(pwd)/usr:/a0/usr:Z" agent-zero-local:ready
