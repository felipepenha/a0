FROM docker.io/agent0ai/agent-zero:ready

# Ensure uv and uvx are installed, executable, and available system-wide
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/
ENV UV_LINK_MODE=copy

# Downgrade cryptography to v46.0.7 to fix the SIGILL crash on Apple Silicon (M4/M5) under applehv
RUN /opt/venv-a0/bin/pip install --no-cache-dir "cryptography<47.0.0"

# Add Agent Zero virtualenv to system PATH
ENV PATH="/opt/venv-a0/bin:$PATH"

# Auto-discover and install CLI-Anything Hub plus ALL packages in packages/
COPY packages/ /opt/packages/
RUN /opt/venv-a0/bin/pip install --no-cache-dir "cli-anything-hub>=0.2.0" && \
    if [ -d /opt/packages ] && [ "$(ls -A /opt/packages 2>/dev/null)" ]; then \
        for pkg in /opt/packages/*; do \
            if [ -d "$pkg" ] && ([ -f "$pkg/pyproject.toml" ] || [ -f "$pkg/setup.py" ]); then \
                echo "Auto-installing package: $pkg" && \
                /opt/venv-a0/bin/pip install --no-cache-dir "$pkg"; \
            fi; \
        done; \
    fi && \
    for bin in /opt/venv-a0/bin/*; do \
        [ -f "$bin" ] && [ -x "$bin" ] && ln -sf "$bin" "/usr/local/bin/$(basename "$bin")" 2>/dev/null || true; \
    done



