# CLI-Anything Notion

Agent-native CLI harness for Notion with macOS desktop deep-linking (`notion://`), conforming to the [HKUDS CLI-Anything](https://github.com/HKUDS/CLI-Anything) standard.

## Installation

### From Local Path
```bash
pip install ./packages/cli-anything-notion
# or with uv:
uv pip install -e ./packages/cli-anything-notion
```

### From Git
```bash
pip install "git+https://github.com/<your-repo>.git#subdirectory=packages/cli-anything-notion"
```

## Quick Start
```bash
# Check local macOS desktop app status
notion-cli app status --json

# Search workspace
notion-cli search "Meeting Notes" --json

# Create page with desktop deep link focus
notion-cli page create --parent <ID> --title "My Notes" --open --json
```
