"""CLI-Anything Notion — Command Line Interface and REPL."""

import functools
import json
import os
import shlex
import sys
from typing import Any, Optional

import click

from cli_anything_notion.api import NotionClientWrapper, resolve_notion_token
from cli_anything_notion.macos import (
    get_desktop_status,
    open_in_notion,
    format_notion_scheme_url,
    format_notion_web_url,
)

# Global context state
_json_mode = False
_active_token: Optional[str] = None


def output(data: Any, message: str = ""):
    """Standardized output handler for CLI-Anything harnesses."""
    if _json_mode:
        click.echo(json.dumps(data, indent=2, default=str))
    else:
        if message:
            click.secho(message, fg="green", bold=True)
        if isinstance(data, dict):
            _print_dict(data)
        elif isinstance(data, list):
            _print_list(data)
        elif data is not None:
            click.echo(str(data))


def _print_dict(d: dict, indent: int = 0):
    prefix = "  " * indent
    for k, v in d.items():
        if isinstance(v, dict):
            click.secho(f"{prefix}{k}:", bold=True)
            _print_dict(v, indent + 1)
        elif isinstance(v, list):
            click.secho(f"{prefix}{k}:", bold=True)
            _print_list(v, indent + 1)
        else:
            click.echo(f"{prefix}{click.style(str(k), fg='cyan')}: {v}")


def _print_list(items: list, indent: int = 0):
    prefix = "  " * indent
    for i, item in enumerate(items):
        if isinstance(item, dict):
            title = item.get("title") or item.get("id") or f"Item {i+1}"
            click.secho(f"{prefix}• {title}", fg="yellow", bold=True)
            _print_dict(item, indent + 1)
        else:
            click.echo(f"{prefix}- {item}")


def handle_errors(func):
    """Decorator to catch and standardize errors for both CLI and agents."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as exc:
            if _json_mode:
                click.echo(
                    json.dumps(
                        {"error": str(exc), "type": exc.__class__.__name__},
                        indent=2,
                    )
                )
            else:
                click.secho(f"Error: {exc}", fg="red", err=True)
            sys.exit(1)

    return wrapper


def get_client() -> NotionClientWrapper:
    return NotionClientWrapper(token=_active_token)


@click.group(invoke_without_command=True)
@click.option("--token", "-t", default=None, help="Notion Internal Integration Token.")
@click.option("--json", "json_output", is_flag=True, help="Emit output as machine-readable JSON.")
@click.option("--repl", is_flag=True, help="Launch interactive REPL session.")
@click.pass_context
def cli(ctx: click.Context, token: Optional[str], json_output: bool, repl: bool):
    """CLI-Anything Notion: Agent-native CLI for Notion with macOS desktop deep-linking."""
    global _json_mode, _active_token
    _json_mode = json_output
    _active_token = token

    if ctx.invoked_subcommand is None or repl:
        ctx.invoke(repl_command)


# -----------------------------------------------------------------------------
# APP DIAGNOSTICS & MACOS INTEGRATION COMMANDS
# -----------------------------------------------------------------------------

@cli.group()
def app():
    """Manage and inspect the local macOS Notion desktop application."""
    pass


@app.command(name="status")
@handle_errors
def app_status():
    """Show diagnostic status of local macOS Notion installation."""
    status = get_desktop_status()
    output(status, message="macOS Notion Desktop Status:")


@app.command(name="open")
@click.argument("target", required=False, default="")
@handle_errors
def app_open(target: str):
    """Launch Notion desktop or open a specific page/database ID via notion://."""
    success, msg = open_in_notion(target if target else "")
    output({"success": success, "message": msg, "target": target}, message=msg)


# -----------------------------------------------------------------------------
# SEARCH COMMANDS
# -----------------------------------------------------------------------------

@cli.command()
@click.argument("query", default="")
@click.option("--type", "filter_type", type=click.Choice(["page", "database"]), default=None)
@click.option("--limit", "-n", default=10, help="Maximum number of results to retrieve.")
@handle_errors
def search(query: str, filter_type: Optional[str], limit: int):
    """Search pages and databases across your Notion workspace."""
    client = get_client()
    results = client.search(query=query, filter_type=filter_type, page_size=limit)
    output(results, message=f"Search results for '{query}':" if query else "Workspace items:")


# -----------------------------------------------------------------------------
# PAGE COMMANDS
# -----------------------------------------------------------------------------

@cli.group()
def page():
    """Manage and inspect Notion pages."""
    pass


@page.command(name="get")
@click.argument("page_id")
@click.option("--open", "open_app", is_flag=True, help="Immediately open page in macOS Notion desktop.")
@handle_errors
def page_get(page_id: str, open_app: bool):
    """Retrieve metadata and top-level block content for a page."""
    client = get_client()
    page_info = client.get_page(page_id)
    if open_app:
        open_in_notion(page_id)
    output(page_info, message=f"Page: {page_info.get('title')}")


@page.command(name="create")
@click.option("--parent", "-p", required=True, help="Parent page or database ID.")
@click.option("--title", "-t", required=True, help="Title of the new page.")
@click.option("--body", "-b", default="", help="Initial body text (markdown paragraphs, callouts, headings).")
@click.option("--database", "is_db", is_flag=True, help="Set if parent is a database.")
@click.option("--properties", "-P", "properties_json", default=None, help="JSON dictionary of database properties (e.g. '{\"Area\": [\"Upper Body\"]}').")
@click.option("--open", "open_app", is_flag=True, help="Immediately open created page in macOS Notion.")
@handle_errors
def page_create(parent: str, title: str, body: str, is_db: bool, properties_json: Optional[str], open_app: bool):
    """Create a new page in Notion."""
    client = get_client()
    created = client.create_page(parent_id=parent, title=title, body=body, is_database=is_db, properties_json=properties_json)
    if open_app and created.get("id"):
        open_in_notion(created["id"])
    output(created, message=f"Successfully created page: {title}")


@page.command(name="append")
@click.argument("page_id")
@click.option("--text", "-t", required=True, help="Text to append.")
@click.option(
    "--type",
    "block_type",
    type=click.Choice(["paragraph", "to_do", "bulleted_list_item", "heading_2"]),
    default="paragraph",
    help="Type of block to append.",
)
@click.option("--checked", is_flag=True, help="For to_do items: mark as checked.")
@click.option("--open", "open_app", is_flag=True, help="Immediately open page in macOS Notion.")
@handle_errors
def page_append(page_id: str, text: str, block_type: str, checked: bool, open_app: bool):
    """Append a new block (paragraph, to-do, list item) to a page."""
    client = get_client()
    result = client.append_block(page_id=page_id, text=text, block_type=block_type, checked=checked)
    if open_app:
        open_in_notion(page_id)
    output(result, message=f"Appended {block_type} block to page {page_id}")


@page.command(name="open")
@click.argument("page_id")
@handle_errors
def page_open(page_id: str):
    """Open a page directly in the local macOS Notion application."""
    success, msg = open_in_notion(page_id)
    output({"success": success, "message": msg, "page_id": page_id}, message=msg)


# -----------------------------------------------------------------------------
# DATABASE COMMANDS
# -----------------------------------------------------------------------------

@cli.group()
def db():
    """Query and inspect Notion databases."""
    pass


@db.command(name="get")
@click.argument("database_id")
@handle_errors
def db_get(database_id: str):
    """Get database metadata and properties."""
    client = get_client()
    db_info = client.get_database(database_id)
    output(db_info, message=f"Database: {db_info.get('title')}")


@db.command(name="query")
@click.argument("database_id")
@click.option("--limit", "-n", default=10, help="Maximum number of rows to retrieve.")
@handle_errors
def db_query(database_id: str, limit: int):
    """Query rows in a Notion database."""
    client = get_client()
    query_result = client.query_database(database_id, page_size=limit)
    output(query_result, message=f"Rows in database {database_id}:")


# -----------------------------------------------------------------------------
# USER COMMANDS
# -----------------------------------------------------------------------------

@cli.group()
def user():
    """Inspect workspace users and bot identities."""
    pass


@user.command(name="me")
@handle_errors
def user_me():
    """Show details of the currently authenticated integration."""
    client = get_client()
    me_data = client.get_me()
    output(me_data, message="Authenticated Integration Identity:")


@user.command(name="list")
@handle_errors
def user_list():
    """List workspace users accessible to the integration."""
    client = get_client()
    users = client.list_users()
    output(users, message="Workspace Users:")


# -----------------------------------------------------------------------------
# INTERACTIVE REPL
# -----------------------------------------------------------------------------

def repl_command():
    """Launch interactive REPL mode conforming to CLI-Anything conventions."""
    click.secho("=" * 60, fg="cyan")
    click.secho("  CLI-Anything: Notion Interactive REPL", fg="cyan", bold=True)
    click.secho("  Type 'help' for commands, or 'exit' / 'quit' to leave.", fg="white")
    click.secho("=" * 60, fg="cyan")

    try:
        from prompt_toolkit import PromptSession
        from prompt_toolkit.history import InMemoryHistory
        session = PromptSession(history=InMemoryHistory())
        use_pt = True
    except ImportError:
        use_pt = False

    while True:
        try:
            if use_pt:
                line = session.prompt("notion> ")
            else:
                line = input("notion> ")
        except (EOFError, KeyboardInterrupt):
            break

        line = line.strip()
        if not line:
            continue
        if line in ("exit", "quit", "q"):
            break
        if line == "help":
            click.echo("Available commands: search, page, db, user, app, exit")
            continue

        try:
            args = shlex.split(line)
            cli.main(args=args, standalone_mode=False)
        except SystemExit:
            pass
        except Exception as e:
            click.secho(f"REPL Error: {e}", fg="red")


def main():
    cli()


if __name__ == "__main__":
    main()
