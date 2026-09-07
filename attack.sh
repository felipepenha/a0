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

echo "Waiting for target container to become ready..."
sleep 3

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="$(pwd)/logs/audit_report_${TIMESTAMP}.log"
LATEST_LOG="$(pwd)/logs/latest.log"

echo ""
echo "--------------------------------------------------------"
echo "✅ Security Sandbox (attack.sh) is up and running!"
echo "--------------------------------------------------------"
echo "Target App (Juice Shop): http://localhost:8080"
echo "Agent Zero UI:           http://localhost:50001"
echo "Log File Output:        $LOG_FILE"
echo "--------------------------------------------------------"
echo ""

# Perform passive security header audit, output to screen and save log
python3 -c "
import urllib.request
import urllib.error
import sys

target_url = 'http://localhost:8080'

print('========================================================')
print('  PASSIVE SECURITY HEADER & METADATA AUDIT REPORT')
print(f'  Target: {target_url}')
print('========================================================\n')

print('[+] Inspecting HTTP Response Headers...')
try:
    req = urllib.request.Request(target_url, method='HEAD')
    with urllib.request.urlopen(req, timeout=10) as resp:
        print(f'  Status Code: {resp.status} {resp.reason}')
        headers = {k.lower(): v for k, v in resp.headers.items()}
        
        print('\n  Observed Headers:')
        for k, v in resp.headers.items():
            print(f'    {k}: {v}')

        print('\n[+] Evaluating Standard Security Headers:')
        sec_headers = {
            'content-security-policy': 'Mitigates Cross-Site Scripting (XSS)',
            'strict-transport-security': 'Enforces HTTPS connections (HSTS)',
            'x-frame-options': 'Protects against Clickjacking attacks',
            'x-content-type-options': 'Prevents MIME-type sniffing',
            'referrer-policy': 'Controls HTTP referrer information exposure',
            'permissions-policy': 'Restricts browser feature usage'
        }

        for header, desc in sec_headers.items():
            if header in headers:
                print(f'  [PASS] {header}: {headers[header]}')
            else:
                print(f'  [MISSING] {header} ({desc})')

except Exception as e:
    print(f'  [!] Failed to query headers: {e}')

print('\n[+] Inspecting Public Configuration Files...')
for path in ['/robots.txt', '/sitemap.xml']:
    file_url = target_url.rstrip('/') + path
    try:
        req = urllib.request.Request(file_url)
        with urllib.request.urlopen(req, timeout=5) as resp:
            content = resp.read().decode('utf-8', errors='ignore')
            print(f'\n  [FOUND] {path} (HTTP {resp.status}, {len(content)} bytes):')
            lines = content.splitlines()[:15]
            for line in lines:
                print(f'    | {line}')
            if len(content.splitlines()) > 15:
                print('    | ... (truncated)')
    except urllib.error.HTTPError as e:
        print(f'  [NOT FOUND] {path} (HTTP {e.code})')
    except Exception as e:
        print(f'  [ERR] {path}: {e}')

print('\n========================================================')
print('  Audit Complete.')
print('========================================================')
" | tee "$LOG_FILE" | tee "$LATEST_LOG"

