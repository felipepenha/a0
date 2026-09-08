"""Unit and integration tests for CLI-Anything Notion harness."""

import json
from unittest.mock import MagicMock, patch
from click.testing import CliRunner
import pytest

from cli_anything_notion.cli import cli
from cli_anything_notion.macos import (
    normalize_notion_id,
    format_notion_scheme_url,
    format_notion_web_url,
    get_desktop_status,
)


def test_id_normalization():
    """Verify UUID and URL parsing correctly extracts 32-char hex string."""
    uuid_with_hyphens = "12345678-abcd-ef01-2345-6789abcdef01"
    assert normalize_notion_id(uuid_with_hyphens) == "12345678abcdef0123456789abcdef01"

    plain_id = "12345678abcdef0123456789abcdef01"
    assert normalize_notion_id(plain_id) == "12345678abcdef0123456789abcdef01"

    full_url = "https://www.notion.so/myworkspace/My-Page-Title-12345678abcdef0123456789abcdef01"
    assert normalize_notion_id(full_url) == "12345678abcdef0123456789abcdef01"


def test_url_scheme_formatting():
    """Verify notion:// deep link URL structure."""
    target_id = "12345678-abcd-ef01-2345-6789abcdef01"
    scheme_url = format_notion_scheme_url(target_id)
    assert scheme_url == "notion://www.notion.so/12345678abcdef0123456789abcdef01"

    web_url = format_notion_web_url(target_id)
    assert web_url == "https://www.notion.so/12345678abcdef0123456789abcdef01"


def test_desktop_status_structure():
    """Verify diagnostic dictionary keys."""
    status = get_desktop_status()
    assert "platform" in status
    assert "is_macos" in status
    assert "installed" in status
    assert "running" in status
    assert "scheme_supported" in status


def test_cli_help():
    """Verify top-level help and subcommands list."""
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "CLI-Anything Notion" in result.output
    assert "search" in result.output
    assert "page" in result.output
    assert "db" in result.output
    assert "app" in result.output


def test_cli_app_status():
    """Verify app status command output."""
    runner = CliRunner()
    result = runner.invoke(cli, ["app", "status"])
    assert result.exit_code == 0
    assert "macOS Notion Desktop Status:" in result.output


def test_cli_app_status_json():
    """Verify --json produces valid parseable JSON."""
    runner = CliRunner()
    result = runner.invoke(cli, ["--json", "app", "status"])
    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert "installed" in payload
    assert "scheme_supported" in payload


def test_missing_token_error_json():
    """Verify missing token produces structured JSON error."""
    runner = CliRunner()
    with patch.dict("os.environ", {}, clear=True):
        result = runner.invoke(cli, ["--json", "search", "test"])
        assert result.exit_code != 0
        payload = json.loads(result.output)
        assert "error" in payload
        assert "token" in payload["error"].lower()


@patch("cli_anything_notion.cli.get_client")
def test_mocked_search_json(mock_get_client):
    """Verify search command with mocked API response."""
    mock_client = MagicMock()
    mock_client.search.return_value = {
        "total_matches": 1,
        "results": [
            {
                "id": "page-123",
                "type": "page",
                "title": "Meeting Notes",
                "url": "https://notion.so/page-123",
            }
        ],
        "has_more": False,
    }
    mock_get_client.return_value = mock_client

    runner = CliRunner()
    result = runner.invoke(cli, ["--json", "search", "Meeting"])
    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["total_matches"] == 1
    assert payload["results"][0]["title"] == "Meeting Notes"


@patch("cli_anything_notion.cli.open_in_notion")
@patch("cli_anything_notion.cli.get_client")
def test_page_get_with_open_flag(mock_get_client, mock_open):
    """Verify page get with --open triggers macOS deep link."""
    mock_client = MagicMock()
    mock_client.get_page.return_value = {
        "id": "p-999",
        "title": "Test Page",
        "blocks": [],
    }
    mock_get_client.return_value = mock_client
    mock_open.return_value = (True, "Opened")

    runner = CliRunner()
    result = runner.invoke(cli, ["page", "get", "p-999", "--open"])
    assert result.exit_code == 0
    mock_open.assert_called_once_with("p-999")


@patch("cli_anything_notion.cli.open_in_notion")
@patch("cli_anything_notion.cli.get_client")
def test_page_create(mock_get_client, mock_open):
    """Verify page creation command arguments and execution."""
    mock_client = MagicMock()
    mock_client.create_page.return_value = {
        "id": "new-page-id",
        "title": "Roadmap Q4",
        "type": "page",
    }
    mock_get_client.return_value = mock_client
    mock_open.return_value = (True, "Opened")

    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "--json",
            "page",
            "create",
            "--parent",
            "parent-123",
            "--title",
            "Roadmap Q4",
            "--body",
            "Section 1 details",
            "--open",
        ],
    )
    assert result.exit_code == 0
    mock_client.create_page.assert_called_once_with(
        parent_id="parent-123",
        title="Roadmap Q4",
        body="Section 1 details",
        is_database=False,
        properties_json=None,
    )
    mock_open.assert_called_once_with("new-page-id")
    payload = json.loads(result.output)
    assert payload["id"] == "new-page-id"

