FROM docker.io/agent0ai/agent-zero:ready

# Downgrade cryptography to v46.0.7 to fix the SIGILL crash on Apple Silicon (M4/M5) under applehv
RUN /opt/venv-a0/bin/pip install --no-cache-dir "cryptography<47.0.0"
