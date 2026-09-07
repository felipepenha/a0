import os
import sys
import time
import json
import urllib.request
import urllib.error
import subprocess

def get_api_key():
    """Retrieve the API key dynamically from the running Podman container."""
    try:
        cmd = [
            "podman", "exec", "attacker",
            "/opt/venv-a0/bin/python", "-c",
            "import sys; sys.path.insert(0, '/a0'); from helpers import settings; print(settings.get_settings().get('mcp_server_token', ''))"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        token = result.stdout.strip()
        if token:
            return token
    except Exception as e:
        print(f"Warning: Could not fetch API token dynamically via podman: {e}", file=sys.stderr)

    return os.environ.get("AGENT0_API_KEY", "")

def send_message(host="http://localhost:50001", prompt="Hello", api_key="", max_wait=120):
    """Send a prompt to Agent Zero via the REST API and wait for the response."""
    url = f"{host.rstrip('/')}/api/api_message"
    headers = {
        "Content-Type": "application/json",
        "X-API-KEY": api_key
    }
    payload = {
        "message": prompt,
        "lifetime_hours": 24
    }

    print(f"[*] Sending prompt to Agent Zero API ({url})...")
    print(f"[*] Prompt: {prompt}\n")

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=max_wait) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="ignore")
        print(f"❌ HTTP Error {e.code}: {error_body}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Request failed: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    prompt = sys.argv[1] if len(sys.argv) > 1 else "Summarize the default environment and available tools."
    host = sys.argv[2] if len(sys.argv) > 2 else "http://localhost:50001"

    api_key = get_api_key()
    if not api_key:
        print("❌ Error: Could not determine Agent Zero API token.", file=sys.stderr)
        sys.exit(1)

    response_data = send_message(host=host, prompt=prompt, api_key=api_key)

    context_id = response_data.get("context_id", "N/A")
    agent_response = response_data.get("response", "")

    print("========================================================")
    print("  AGENT ZERO SESSION RESPONSE REPORT")
    print(f"  Context ID: {context_id}")
    print("========================================================\n")
    print(agent_response)
    print("\n========================================================")

if __name__ == "__main__":
    main()
