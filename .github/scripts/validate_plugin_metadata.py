#!/usr/bin/env python3
"""Validate plugin metadata and skill frontmatter."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PLUGINS_DIR = REPO_ROOT / "plugins"
MARKETPLACE_JSON = REPO_ROOT / ".claude-plugin" / "marketplace.json"


def validate_frontmatter(skill_md: Path) -> list[str]:
    """Validate SKILL.md frontmatter."""
    errors = []
    content = skill_md.read_text()
    
    # Check for frontmatter
    if not content.startswith("---"):
        errors.append(f"{skill_md}: Missing YAML frontmatter")
        return errors
    
    # Extract frontmatter
    match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not match:
        errors.append(f"{skill_md}: Invalid frontmatter format")
        return errors
    
    frontmatter = match.group(1)
    
    # Check required fields
    if "name:" not in frontmatter:
        errors.append(f"{skill_md}: Missing 'name' in frontmatter")
    if "description:" not in frontmatter:
        errors.append(f"{skill_md}: Missing 'description' in frontmatter")
    
    # Check name format
    name_match = re.search(r"name:\s*([^\n]+)", frontmatter)
    if name_match:
        name = name_match.group(1).strip().strip('"\'')
        if not re.match(r"^[a-z0-9-]+$", name):
            errors.append(f"{skill_md}: Name '{name}' must be kebab-case")
        if len(name) > 64:
            errors.append(f"{skill_md}: Name '{name}' exceeds 64 characters")
    
    return errors


def validate_plugin_json(plugin_json: Path) -> list[str]:
    """Validate plugin.json."""
    errors = []
    
    try:
        data = json.loads(plugin_json.read_text())
    except json.JSONDecodeError as e:
        errors.append(f"{plugin_json}: Invalid JSON: {e}")
        return errors
    
    required = ["name", "version", "description"]
    for field in required:
        if field not in data:
            errors.append(f"{plugin_json}: Missing required field '{field}'")
    
    return errors


def validate_marketplace() -> list[str]:
    """Validate marketplace.json."""
    errors = []
    
    if not MARKETPLACE_JSON.exists():
        errors.append(f"Missing {MARKETPLACE_JSON}")
        return errors
    
    try:
        data = json.loads(MARKETPLACE_JSON.read_text())
    except json.JSONDecodeError as e:
        errors.append(f"{MARKETPLACE_JSON}: Invalid JSON: {e}")
        return errors
    
    # Check structure
    if "plugins" not in data:
        errors.append(f"{MARKETPLACE_JSON}: Missing 'plugins' array")
        return errors
    
    # Check each plugin is registered
    plugin_dirs = [d.name for d in PLUGINS_DIR.iterdir() if d.is_dir()]
    registered = {p["name"] for p in data["plugins"]}
    
    for plugin_name in plugin_dirs:
        if plugin_name not in registered:
            errors.append(
                f"Plugin '{plugin_name}' not registered in marketplace.json"
            )
    
    return errors


def main() -> int:
    errors: list[str] = []
    
    # Validate marketplace
    errors.extend(validate_marketplace())
    
    # Validate each plugin
    for plugin_dir in sorted(PLUGINS_DIR.iterdir()):
        if not plugin_dir.is_dir():
            continue
        
        # Check plugin.json
        plugin_json = plugin_dir / ".claude-plugin" / "plugin.json"
        if plugin_json.exists():
            errors.extend(validate_plugin_json(plugin_json))
        else:
            errors.append(f"Missing {plugin_json}")
        
        # Check skills
        skills_dir = plugin_dir / "skills"
        if skills_dir.exists():
            for skill_dir in skills_dir.iterdir():
                if not skill_dir.is_dir():
                    continue
                skill_md = skill_dir / "SKILL.md"
                if skill_md.exists():
                    errors.extend(validate_frontmatter(skill_md))
                else:
                    errors.append(f"Missing SKILL.md in {skill_dir}")
    
    if errors:
        print("Plugin validation failed:\n", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1
    
    print("✓ All plugin metadata validated successfully")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
