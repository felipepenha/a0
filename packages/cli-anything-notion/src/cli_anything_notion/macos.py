"""macOS integration utilities for Notion desktop application."""

import os
import re
import shutil
import subprocess
import sys
from typing import Optional, Tuple

NOTION_APP_PATHS = [
    "/Applications/Notion.app",
    os.path.expanduser("~/Applications/Notion.app"),
]


def is_macos() -> bool:
    """Check if current operating system is macOS."""
    return sys.platform == "darwin"


def find_notion_app() -> Optional[str]:
    """Locate the Notion desktop app on macOS."""
    if not is_macos():
        return None
    for path in NOTION_APP_PATHS:
        if os.path.exists(path):
            return path
    return None


def is_notion_running() -> bool:
    """Check if Notion desktop app is currently running."""
    if not is_macos():
        return False
    try:
        res = subprocess.run(
            ["pgrep", "-x", "Notion"],
            capture_output=True,
            text=True,
            check=False,
        )
        return res.returncode == 0
    except Exception:
        return False


def normalize_notion_id(target: str) -> str:
    """Normalize a Notion page or database ID (strip hyphens and URLs)."""
    # If a full URL is passed, extract the ID component
    if "notion.so" in target:
        match = re.search(r"([0-9a-fA-F]{32}|[0-9a-fA-F-]{36})", target)
        if match:
            target = match.group(1)
    # Remove hyphens
    clean_id = target.replace("-", "").strip()
    return clean_id


def format_notion_scheme_url(target: str) -> str:
    """Create a notion:// desktop scheme URL from an ID or path."""
    clean_id = normalize_notion_id(target)
    return f"notion://www.notion.so/{clean_id}"


def format_notion_web_url(target: str) -> str:
    """Create a standard https://notion.so URL from an ID or path."""
    clean_id = normalize_notion_id(target)
    return f"https://www.notion.so/{clean_id}"


def open_in_notion(target: str, prefer_native: bool = True) -> Tuple[bool, str]:
    """
    Open a page or database in the local macOS Notion app.
    
    Returns:
        (success, message)
    """
    if not is_macos():
        return False, "Deep linking to Notion desktop is only supported on macOS."

    app_path = find_notion_app()
    target_url = format_notion_scheme_url(target) if prefer_native else format_notion_web_url(target)

    cmd = ["open", target_url]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if proc.returncode == 0:
            app_info = f" ({app_path})" if app_path else ""
            return True, f"Opened {target_url} in Notion desktop{app_info}."
        else:
            # Fallback to open -a Notion <web_url> if scheme failed
            if app_path:
                web_url = format_notion_web_url(target)
                fallback_proc = subprocess.run(
                    ["open", "-a", app_path, web_url],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                if fallback_proc.returncode == 0:
                    return True, f"Opened {web_url} in Notion app fallback."
            return False, f"Failed to open URL: {proc.stderr.strip()}"
    except Exception as exc:
        return False, f"Error opening Notion: {exc}"


def get_desktop_status() -> dict:
    """Retrieve diagnostic state of macOS Notion installation."""
    app_path = find_notion_app()
    running = is_notion_running()
    return {
        "platform": sys.platform,
        "is_macos": is_macos(),
        "installed": app_path is not None,
        "app_path": app_path or "Not found",
        "running": running,
        "scheme_supported": is_macos() and app_path is not None,
    }
