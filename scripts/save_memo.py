"""Save the latest memo from a project as a clean Markdown file.

Usage:
    python scripts/save_memo.py PROJECT_ID
    python scripts/save_memo.py  # uses demo project
"""

from __future__ import annotations

import json
import re
import sys
import httpx

API = "http://localhost:8000"
DEMO_PROJECT = "9b7d36e6-b590-49f6-8439-2d702ac5a9f6"


def extract_markdown(content: str) -> str:
    """Extract clean markdown from memo content.

    Handles both:
    - Clean markdown (new memos after parser fix)
    - Raw JSON with payloads[].text (old memos before parser fix)
    """
    # If it looks like JSON, try to extract the text payload
    stripped = content.strip()
    if stripped.startswith("{") or stripped.startswith("["):
        try:
            obj = json.loads(stripped)
            if isinstance(obj, dict) and "payloads" in obj:
                parts = [p["text"] for p in obj["payloads"] if p.get("text")]
                if parts:
                    return "\n\n".join(parts)
        except json.JSONDecodeError:
            pass

    # Check for literal \n (escaped newlines stored as text)
    if "\\n" in content and "\n" not in content.rstrip("\\n"):
        content = content.encode().decode("unicode_escape")

    # Strip any trailing JSON metadata that leaked in
    # Look for a line starting with "mediaUrl" or "meta" after the markdown
    for marker in ['\n"mediaUrl"', '\n,"mediaUrl"', '\n"meta"', '\n,\n"meta"']:
        idx = content.find(marker)
        if idx != -1:
            content = content[:idx]

    return content.strip()


def main():
    project_id = sys.argv[1] if len(sys.argv) > 1 else DEMO_PROJECT

    resp = httpx.get(f"{API}/projects/{project_id}/memos")
    resp.raise_for_status()
    memos = resp.json()

    if not memos:
        print("No memos found for this project.")
        sys.exit(1)

    memo = memos[0]
    markdown = extract_markdown(memo["content_markdown"])

    slug = re.sub(r"[^\w\s-]", "", memo["title"]).strip().replace(" ", "_")
    filename = f"{slug}.md"

    with open(filename, "w") as f:
        f.write(markdown + "\n")

    print(f"Saved: {filename} ({len(markdown)} chars)")


if __name__ == "__main__":
    main()
