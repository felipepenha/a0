#!/bin/bash

# Stop and remove existing containers and network to ensure a clean start
podman stop vulnerable_container attacker >/dev/null 2>&1
podman rm vulnerable_container attacker >/dev/null 2>&1
podman network rm sec_test_net >/dev/null 2>&1

# Create a network for the containers
podman network create --driver bridge sec_test_net

# Run the vulnerable target container
echo "Starting target container..."
podman pull bkimminich/juice-shop
podman run -d --name vulnerable_container --net sec_test_net -p 8080:3000 bkimminich/juice-shop

# Ensure persistent user data directory exists on host
mkdir -p "$(pwd)/usr"

# Run the agent0 container (using patched image with persistent volume)
echo "Building patched Agent Zero image..."
podman build -t agent-zero-local:ready .

echo "Starting Agent Zero container..."
podman run -d --name attacker --net sec_test_net -p 50001:80 -v "$(pwd)/usr:/a0/usr:Z" agent-zero-local:ready

echo ""
echo "--------------------------------------------------------"
echo "✅ Security Sandbox (attack.sh) is up and running!"
echo "--------------------------------------------------------"
echo "Target App (Juice Shop): http://localhost:8080"
echo "Agent Zero UI:           http://localhost:50001"
echo ""
echo "Passive Reconnaissance Prompt for Agent Zero Web UI:"
echo ""
echo 'Inspect the main HTTP response headers and public configuration files'
echo '(such as robots.txt and sitemap.xml) at http://vulnerable_container:3000.'
echo 'Check for the presence of standard security headers (like Content-Security-Policy,'
echo 'X-Frame-Options, and Strict-Transport-Security) and summarize the findings passively.'
echo "--------------------------------------------------------"
echo ""
