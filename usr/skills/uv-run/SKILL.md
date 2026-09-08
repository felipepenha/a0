---
name: uv-run
description: "Instructs agents on how to leverage uv (uv run, uv sync, uv add, uvx) to manage dependencies and execute Python scripts whenever a pyproject.toml or PEP 723 inline script metadata is present. Enforces isolated virtual environments and strictly prohibits global pip installations or modifying base system environments."
---

# Leveraging `uv` for Python Execution and Dependency Management

Use this skill whenever you need to execute Python scripts, run test suites, or manage Python packages in a project that contains a `pyproject.toml` file, or when working with standalone scripts that specify dependencies.

## Core Directives

1. **Never use `pip install` globally**: Do NOT run `pip install` or `/opt/venv-a0/bin/pip install` in the container. Global package installations pollute the system and cause version conflicts.
2. **Always prefer `uv run`**: Whenever a `pyproject.toml` exists in the current directory, a parent directory, or a subproject folder, run scripts via `uv run`.
3. **Isolate environments per project**: `uv` automatically creates and caches an isolated `.venv` local to the project.
4. **Use `--project` for remote paths**: If the current working directory is not the directory containing `pyproject.toml`, pass `--project <path-to-folder-with-pyproject.toml>`.

---

## Standard Workflows & Commands

### 1. Running Scripts (`uv run`)

`uv run` ensures all dependencies declared in `pyproject.toml` are installed and up to date in the local virtual environment before running the command.

```bash
# When inside the directory containing pyproject.toml:
uv run python script.py [args...]

# When running from another directory:
uv run --project /path/to/project/ python /path/to/project/script.py [args...]

# Example: Running a tool from a specific project path
uv run --project packages/cli-anything-notion notion-cli page create --title "My Workout"
```

### 2. Synchronizing Dependencies (`uv sync`)

`uv sync` ensures that the project's `.venv` exactly matches the dependencies declared in `pyproject.toml` and locked in `uv.lock`.

```bash
# Sync dependencies in the current project directory:
uv sync

# Sync dependencies for a specific project path:
uv sync --project /path/to/project/

# Sync including optional dependency groups or extras (e.g., dev/test):
uv sync --all-extras
```

> **Note**: `uv run` automatically performs synchronization on the fly if dependencies are missing, but `uv sync` is recommended when setting up or preparing an environment ahead of time.

### 3. Adding or Removing Dependencies

Always update `pyproject.toml` using `uv add` or `uv remove` rather than modifying the file by hand or installing via `pip`:

```bash
# Add a new dependency
uv add requests
uv add --project /path/to/project/ notion-client

# Add development / testing dependencies
uv add --dev pytest

# Remove a dependency
uv remove requests
uv remove --project /path/to/project/ old-package
```

### 4. Running Tools & CLIs Defined in Projects

If a project's `pyproject.toml` registers console scripts or tools (e.g. `pytest`, `ruff`, or a custom CLI):

```bash
# Run registered CLI entrypoints directly:
uv run pytest
uv run notion-cli --help

# From another directory:
uv run --project /path/to/project pytest /path/to/project/tests
```

### 5. Running One-Off Tools with `uvx`

To execute an ephemeral command-line tool without adding it to the project's dependencies:

```bash
uvx ruff check .
uvx black --check .
```

---

## Detecting `pyproject.toml` Hierarchy

Before running any Python command:
1. Check if the current directory has a `pyproject.toml`:
   - Run `ls pyproject.toml` or check directory contents.
   - If present: execute `uv run python ...`.
2. Check if a parent or subproject directory has `pyproject.toml`:
   - For skills: check `<skill>/scripts/pyproject.toml`.
   - If present: execute `uv run --project <dir> python ...`.
3. Check for PEP 723 inline script metadata:
   - If the script header starts with `# /// script`, `uv run script.py` will read the dependencies directly from the script without requiring a separate `pyproject.toml`.

---

## Troubleshooting & Container Notes

- **Volume Mounts**: In containerized environments where files are mounted across host/container boundaries, `ENV UV_LINK_MODE=copy` is pre-configured to avoid hardlink issues.
- **Cache**: `uv` caches wheels and metadata in `~/.cache/uv`. Subsequent executions are instantaneous (under 50ms).
- **Virtual Environment location**: The `.venv` directory created by `uv` resides inside the directory containing `pyproject.toml`. Do not commit `.venv` to version control.
