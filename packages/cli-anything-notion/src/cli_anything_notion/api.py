"""Notion API integration wrapper."""

import os
from typing import Any, Dict, List, Optional
from notion_client import Client
from notion_client.errors import APIResponseError

from cli_anything_notion.macos import normalize_notion_id


def resolve_notion_token(explicit_token: Optional[str] = None) -> str:
    """
    Resolve Notion token from explicit argument, environment, or .env files.
    """
    if explicit_token and explicit_token.strip():
        return explicit_token.strip()

    # Check environment variables
    env_token = os.environ.get("NOTION_TOKEN") or os.environ.get("NOTION_API_KEY")
    if env_token and env_token.strip():
        return env_token.strip()

    # Check local .env files
    candidate_paths = [
        os.path.join(os.getcwd(), ".env"),
        os.path.join(os.getcwd(), "usr", ".env"),
        os.path.expanduser("~/.config/notion/token"),
    ]
    for path in candidate_paths:
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as fp:
                    for line in fp:
                        line = line.strip()
                        if line.startswith("NOTION_TOKEN=") or line.startswith("NOTION_API_KEY="):
                            _, val = line.split("=", 1)
                            val = val.strip().strip('"').strip("'")
                            if val:
                                return val
                        # Plain token file
                        elif not line.startswith("#") and line.startswith("ntn_"):
                            return line
            except Exception:
                continue

    return ""


class NotionClientWrapper:
    """Structured high-level client for Notion API operations."""

    def __init__(self, token: Optional[str] = None):
        resolved_token = resolve_notion_token(token)
        if not resolved_token:
            raise ValueError(
                "Notion token not found. Please provide --token, set the NOTION_TOKEN environment "
                "variable, or add NOTION_TOKEN to your .env file."
            )
        self.token = resolved_token
        self.client = Client(auth=self.token)

    def search(
        self,
        query: str = "",
        filter_type: Optional[str] = None,
        page_size: int = 10,
    ) -> Dict[str, Any]:
        """Search workspace pages and databases by query."""
        kwargs: Dict[str, Any] = {"page_size": min(page_size, 100)}
        if query:
            kwargs["query"] = query
        if filter_type in ("page", "database"):
            kwargs["filter"] = {"value": filter_type, "property": "object"}

        response = self.client.search(**kwargs)
        results = []
        for item in response.get("results", []):
            results.append(self._summarize_object(item))
        return {
            "total_matches": len(results),
            "results": results,
            "has_more": response.get("has_more", False),
        }

    def get_page(self, page_id: str) -> Dict[str, Any]:
        """Retrieve page metadata and top-level block children."""
        clean_id = normalize_notion_id(page_id)
        page_data = self.client.pages.retrieve(page_id=clean_id)
        
        # Retrieve child blocks for content preview
        blocks = []
        try:
            block_children = self.client.blocks.children.list(block_id=clean_id, page_size=20)
            for b in block_children.get("results", []):
                b_type = b.get("type", "unknown")
                text_content = self._extract_block_text(b, b_type)
                blocks.append({"id": b.get("id"), "type": b_type, "text": text_content})
        except Exception:
            pass

        summary = self._summarize_object(page_data)
        summary["blocks"] = blocks
        return summary

    def create_page(
        self,
        parent_id: str,
        title: str,
        body: str = "",
        is_database: bool = False,
        properties_json: Optional[Any] = None,
    ) -> Dict[str, Any]:
        """Create a new page under a parent page or database."""
        clean_parent_id = normalize_notion_id(parent_id)

        parent: Dict[str, Any]
        properties: Dict[str, Any]

        if is_database:
            parent = {"database_id": clean_parent_id}
            title_prop_name = "Name"
            try:
                db_meta = self.client.databases.retrieve(database_id=clean_parent_id)
                for prop_name, prop_data in db_meta.get("properties", {}).items():
                    if prop_data.get("type") == "title":
                        title_prop_name = prop_name
                        break
            except Exception:
                pass
            properties = {
                title_prop_name: {
                    "title": [{"type": "text", "text": {"content": title}}]
                }
            }
            if properties_json:
                import json
                extra_props = json.loads(properties_json) if isinstance(properties_json, str) else properties_json
                if isinstance(extra_props, dict):
                    for key, val in extra_props.items():
                        if key.lower() in (title_prop_name.lower(), "title"):
                            continue
                        if isinstance(val, dict) and any(k in val for k in ("multi_select", "select", "rich_text", "number", "url")):
                            properties[key] = val
                        elif isinstance(val, list):
                            properties[key] = {"multi_select": [{"name": str(item)} for item in val]}
                        elif isinstance(val, (int, float)):
                            properties[key] = {"number": val}
                        elif isinstance(val, str):
                            properties[key] = {"rich_text": [{"type": "text", "text": {"content": val}}]}
        else:
            parent = {"page_id": clean_parent_id}
            properties = {
                "title": {
                    "title": [{"type": "text", "text": {"content": title}}]
                }
            }

        children = self.parse_markdown_to_blocks(body) if body else []

        payload = {"parent": parent, "properties": properties}
        if children:
            payload["children"] = children[:100]  # Notion API limit per request

        new_page = self.client.pages.create(**payload)
        return self._summarize_object(new_page)

    @staticmethod
    def parse_markdown_to_blocks(content: str) -> List[Dict[str, Any]]:
        """Parse structured text / markdown into Notion block objects."""
        import re
        blocks = []
        # Pattern for <callout icon="📖" color="blue_bg">text</callout>
        callout_pattern = re.compile(r'<callout(?:\s+icon="([^"]*)")?(?:\s+color="([^"]*)")?>([\s\S]*?)</callout>', re.IGNORECASE)
        # Pattern for <video src="URL">caption</video>
        video_pattern = re.compile(r'<video\s+src="([^"]+)">([\s\S]*?)</video>', re.IGNORECASE)

        remaining = content.strip()
        paragraphs = re.split(r'\n\s*\n', remaining)

        for p in paragraphs:
            p = p.strip()
            if not p:
                continue

            callout_match = callout_pattern.search(p)
            if callout_match:
                icon_char = callout_match.group(1) or "💡"
                color_name = callout_match.group(2) or "default"
                callout_text = callout_match.group(3).strip()
                callout_block: Dict[str, Any] = {
                    "object": "block",
                    "type": "callout",
                    "callout": {
                        "rich_text": [{"type": "text", "text": {"content": callout_text[:2000]}}],
                        "color": color_name if color_name.endswith("_background") or color_name.endswith("_bg") else "blue_background",
                    },
                }
                if icon_char:
                    callout_block["callout"]["icon"] = {"type": "emoji", "emoji": icon_char}
                blocks.append(callout_block)
                continue

            video_match = video_pattern.search(p)
            if video_match:
                video_url = video_match.group(1).strip()
                caption_text = video_match.group(2).strip()
                video_block: Dict[str, Any] = {
                    "object": "block",
                    "type": "video",
                    "video": {
                        "type": "external",
                        "external": {"url": video_url},
                    },
                }
                if caption_text:
                    video_block["video"]["caption"] = [{"type": "text", "text": {"content": caption_text[:2000]}}]
                blocks.append(video_block)
                continue

            if p == "---" or p == "***":
                blocks.append({"object": "block", "type": "divider", "divider": {}})
            elif p.startswith("### "):
                blocks.append({
                    "object": "block",
                    "type": "heading_3",
                    "heading_3": {"rich_text": [{"type": "text", "text": {"content": p[4:][:2000]}}]},
                })
            elif p.startswith("## "):
                blocks.append({
                    "object": "block",
                    "type": "heading_2",
                    "heading_2": {"rich_text": [{"type": "text", "text": {"content": p[3:][:2000]}}]},
                })
            elif p.startswith("# "):
                blocks.append({
                    "object": "block",
                    "type": "heading_1",
                    "heading_1": {"rich_text": [{"type": "text", "text": {"content": p[2:][:2000]}}]},
                })
            elif p.startswith("- [ ] ") or p.startswith("- [x] "):
                checked = p.startswith("- [x] ")
                blocks.append({
                    "object": "block",
                    "type": "to_do",
                    "to_do": {
                        "rich_text": [{"type": "text", "text": {"content": p[6:][:2000]}}],
                        "checked": checked,
                    },
                })
            elif p.startswith("- ") or p.startswith("* "):
                blocks.append({
                    "object": "block",
                    "type": "bulleted_list_item",
                    "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": p[2:][:2000]}}]},
                })
            else:
                blocks.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {"rich_text": [{"type": "text", "text": {"content": p[:2000]}}]},
                })

        return blocks

    def append_block(
        self,
        page_id: str,
        text: str,
        block_type: str = "paragraph",
        checked: bool = False,
    ) -> Dict[str, Any]:
        """Append a new block (paragraph, to_do, bullet, heading) to a page."""
        clean_id = normalize_notion_id(page_id)
        rich_text = [{"type": "text", "text": {"content": text[:2000]}}]

        block_payload: Dict[str, Any]
        if block_type == "to_do":
            block_payload = {
                "object": "block",
                "type": "to_do",
                "to_do": {"rich_text": rich_text, "checked": checked},
            }
        elif block_type in ("heading_1", "heading_2", "heading_3"):
            block_payload = {
                "object": "block",
                "type": block_type,
                block_type: {"rich_text": rich_text},
            }
        elif block_type == "bulleted_list_item":
            block_payload = {
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {"rich_text": rich_text},
            }
        else:
            block_payload = {
                "object": "block",
                "type": "paragraph",
                "paragraph": {"rich_text": rich_text},
            }

        res = self.client.blocks.children.append(
            block_id=clean_id,
            children=[block_payload],
        )
        return {
            "page_id": clean_id,
            "appended_blocks": len(res.get("results", [])),
            "results": res.get("results", []),
        }

    def get_database(self, database_id: str) -> Dict[str, Any]:
        """Retrieve database schema and details."""
        clean_id = normalize_notion_id(database_id)
        db_data = self.client.databases.retrieve(database_id=clean_id)
        return self._summarize_object(db_data)

    def query_database(
        self,
        database_id: str,
        page_size: int = 10,
    ) -> Dict[str, Any]:
        """Query rows in a database."""
        clean_id = normalize_notion_id(database_id)
        res = self.client.databases.query(
            database_id=clean_id,
            page_size=min(page_size, 100),
        )
        rows = [self._summarize_object(r) for r in res.get("results", [])]
        return {
            "database_id": clean_id,
            "total_rows": len(rows),
            "rows": rows,
            "has_more": res.get("has_more", False),
        }

    def get_me(self) -> Dict[str, Any]:
        """Get information about the current integration bot user."""
        return self.client.users.me()

    def list_users(self) -> List[Dict[str, Any]]:
        """List workspace users accessible to the integration."""
        res = self.client.users.list()
        return res.get("results", [])

    def _summarize_object(self, obj: Dict[str, Any]) -> Dict[str, Any]:
        obj_id = obj.get("id", "")
        obj_type = obj.get("object", "unknown")
        url = obj.get("url", f"https://www.notion.so/{normalize_notion_id(obj_id)}")
        
        title = "Untitled"
        if obj_type == "page":
            props = obj.get("properties", {})
            for p in props.values():
                if p.get("type") == "title" and p.get("title"):
                    title = "".join(t.get("plain_text", "") for t in p["title"])
                    break
        elif obj_type == "database":
            title_list = obj.get("title", [])
            if title_list:
                title = "".join(t.get("plain_text", "") for t in title_list)

        return {
            "id": obj_id,
            "type": obj_type,
            "title": title or "Untitled",
            "url": url,
            "created_time": obj.get("created_time"),
            "last_edited_time": obj.get("last_edited_time"),
            "archived": obj.get("archived", False),
        }

    def _extract_block_text(self, block: Dict[str, Any], block_type: str) -> str:
        data = block.get(block_type, {})
        rich_text = data.get("rich_text", [])
        if rich_text:
            return "".join(t.get("plain_text", "") for t in rich_text)
        return ""
