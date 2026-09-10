#!/usr/bin/env python3
"""The capability directory: catalog.json, and the files generated from it.

What a capability IS - its endpoint, how it authenticates, what it costs - cannot be crawled,
so catalog.json is edited by hand and reviewed by pull request. From it, and from the indexes
and guides already in this repository, this module renders:

- llms.txt at the repository root: the one URL an agent needs;
- directory.md: every capability with all its fields, for people and for LLM ingesters;
- the blocks between the markers in README.md;
- casper-guides/llms.txt: the index of the guides written for this repository.

Rendering reads only local files, so a contributor can regenerate without the full crawl
(python scripts/generate.py --catalog-only), and validate.py can tell when a committed file no
longer matches what the catalog produces.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SELF_REPO, SELF_REF = "msanlisavas/casper-llms", "main"
RAW = f"https://raw.githubusercontent.com/{SELF_REPO}/{SELF_REF}/"
BLOB = f"https://github.com/{SELF_REPO}/blob/{SELF_REF}/"
GUIDES_INDEX = "casper-guides/llms.txt"

# kind -> (section heading, singular label). Also the order sections appear in.
KINDS = {
    "llms-txt": ("Documentation indexes", "llms.txt"),
    "mcp-server": ("MCP servers", "MCP server"),
    "agent-skill": ("Agent skills", "Agent skill"),
    "plugin": ("Plugins", "Plugin"),
    "api": ("APIs and payments", "API"),
    "sdk": ("SDKs and libraries", "SDK"),
}
AUTH = {"none": "no key", "api-key": "API key", "x402": "x402 per call", "oauth": "OAuth"}
NETWORKS = {"casper:casper": "mainnet", "casper:casper-test": "testnet"}
TRANSPORTS = {"streamable-http": "Streamable HTTP", "stdio": "stdio", "sse": "SSE"}
PRICING = {"free": "Free", "paid": "Paid", "free-and-paid": "Free and paid"}

# Release lines a guide can be verified against. check.py looks up the latest of each; a guide
# naming anything else could never be flagged as stale, so validate.py refuses it.
COMPONENTS = ("casper-node", "casper-client-rs", "docs.casper.network")

# Our indexes in reading order; any other folder with an llms.txt follows alphabetically.
INDEX_ORDER = ("casper-docs", "casper-guides", "casper-node-tools", "casper-sdks", "casper-standards",
               "casper-ceps", "odra", "casper-x402", "casper-agent-tools")


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


# ----------------------------------------------------------------------------- schema

SUPPORTED = {"$schema", "$id", "$defs", "$ref", "title", "description", "type", "properties", "required",
             "additionalProperties", "items", "enum", "const", "pattern", "minLength", "maxLength",
             "minItems", "uniqueItems", "allOf", "if", "then"}
TYPES = {"object": dict, "array": list, "string": str, "boolean": bool}


def schema_errors(value, schema: dict, root: dict, where: str) -> list[str]:
    """A JSON Schema checker for exactly the keywords catalog.schema.json uses. An unknown keyword
    raises rather than being ignored, so the schema cannot promise a rule nothing enforces."""
    unknown = set(schema) - SUPPORTED
    if unknown:
        raise ValueError(f"catalog.schema.json uses unsupported keywords {sorted(unknown)} at {where}")
    if "$ref" in schema:
        return schema_errors(value, root["$defs"][schema["$ref"].removeprefix("#/$defs/")], root, where)
    expected = schema.get("type")
    if expected and not isinstance(value, TYPES[expected]):
        return [f"{where}: expected {expected}"]
    errors: list[str] = []
    if "const" in schema and value != schema["const"]:
        errors.append(f"{where}: must be {schema['const']!r}")
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{where}: {value!r} is not one of {', '.join(map(str, schema['enum']))}")
    if isinstance(value, str):
        if "pattern" in schema and not re.search(schema["pattern"], value):
            errors.append(f"{where}: {value!r} does not match {schema['pattern']}")
        if len(value) < schema.get("minLength", 0):
            errors.append(f"{where}: shorter than {schema['minLength']} characters")
        if "maxLength" in schema and len(value) > schema["maxLength"]:
            errors.append(f"{where}: longer than {schema['maxLength']} characters ({len(value)})")
    if isinstance(value, list):
        if len(value) < schema.get("minItems", 0):
            errors.append(f"{where}: needs at least {schema['minItems']} item(s)")
        if schema.get("uniqueItems") and len({json.dumps(v, sort_keys=True) for v in value}) < len(value):
            errors.append(f"{where}: has duplicate items")
        for number, item in enumerate(value):
            if "items" in schema:
                errors += schema_errors(item, schema["items"], root, f"{where}[{number}]")
    if isinstance(value, dict):
        errors += [f"{where}: missing required field {key!r}" for key in schema.get("required", []) if key not in value]
        properties = schema.get("properties", {})
        for key, item in value.items():
            if key in properties:
                errors += schema_errors(item, properties[key], root, f"{where}.{key}")
            elif schema.get("additionalProperties") is False:
                errors.append(f"{where}: unknown field {key!r}")
    for sub in schema.get("allOf", []):
        errors += schema_errors(value, sub, root, where)
    if "if" in schema and not schema_errors(value, schema["if"], root, where):
        errors += schema_errors(value, schema.get("then", {}), root, where)
    return errors


def check_catalog(data: dict, schema: dict, reserved: set[str] = frozenset()) -> list[str]:
    """Schema errors first: the cross-entry rules below assume a well-formed catalog."""
    errors = schema_errors(data, schema, schema, "catalog.json")
    if errors:
        return errors
    ids: set[str] = set()
    fetched = set(reserved)
    for number, entry in enumerate(data["capabilities"]):
        where = f"catalog.json capabilities[{number}] ({entry['id']})"
        if entry["id"] in ids:
            errors.append(f"{where}: id is used twice")
        ids.add(entry["id"])
        # The root llms.txt lists every docs.fetch once, and validate.py rejects a repeated fetch URL.
        fetch = entry["docs"]["fetch"]
        if fetch in fetched:
            errors.append(f"{where}: docs.fetch {fetch} is already listed")
        fetched.add(fetch)
        if entry["kind"] == "llms-txt" and fetch != entry["url"]:
            errors.append(f"{where}: an llms-txt entry is its own documentation, so docs.fetch must equal url")
    return errors


# ----------------------------------------------------------------------------- local files

@dataclass
class LocalIndex:
    path: str       # "casper-docs/llms.txt"
    title: str
    summary: str
    pages: int


@dataclass
class Guide:
    path: str                  # "guides/casper-2.1-and-2.2.md"
    title: str
    verified: str              # "Verified against casper-node v2.2.2 on 2026-09-10."
    versions: dict[str, str]   # {"casper-node": "v2.2.2"}


VERIFIED = re.compile(r"^Verified against (?P<what>.+) on (?P<date>\d{4}-\d{2}-\d{2})\.$")
COMPONENT = re.compile(r"(?P<name>[A-Za-z][A-Za-z0-9.\-]*) (?P<version>v?\d+(?:\.\d+)+)")


def parse_index(path: str, text: str) -> LocalIndex:
    title = re.search(r"^# (.+)$", text, re.M)
    quote = re.search(r"^> (.+)$", text, re.M)
    return LocalIndex(path, title.group(1).strip() if title else path, quote.group(1).strip() if quote else "",
                      sum(1 for line in text.splitlines() if line.startswith("- [")))


def parse_guide(path: str, text: str) -> tuple[Guide | None, list[str]]:
    lines = text.splitlines()
    errors = []
    if not lines or not lines[0].startswith("# "):
        errors.append(f"{path}: must start with an H1 ('# '), with no frontmatter")
    match = VERIFIED.match(lines[2].strip()) if len(lines) > 2 and not lines[1].strip() else None
    if not match:
        errors.append(f"{path}: line 3 must read 'Verified against <component> <version>[ and ...] on YYYY-MM-DD.' "
                      "after a blank line 2")
    versions = dict(COMPONENT.findall(match.group("what"))) if match else {}
    if match and not versions:
        errors.append(f"{path}: the verification line names no component and version")
    errors += [f"{path}: the weekly check cannot follow {name}; use one of {', '.join(COMPONENTS)}"
               for name in versions if name not in COMPONENTS]
    if re.search(r"<(html|head|body|div|span|script|table|details)\b", text, re.I):
        errors.append(f"{path}: contains HTML")
    if errors:
        return None, errors
    return Guide(path, lines[0][2:].strip(), lines[2].strip(), versions), []


def local_guides(root: Path = ROOT) -> tuple[list[Guide], list[str]]:
    guides, errors = [], []
    for file in sorted((root / "guides").glob("*.md")):
        guide, problems = parse_guide(file.relative_to(root).as_posix(), file.read_text(encoding="utf-8"))
        errors += problems
        if guide:
            guides.append(guide)
    return guides, errors


def reserved_fetch_urls(root: Path, guides: list[Guide]) -> set[str]:
    """Fetch URLs the root llms.txt lists for this repository's own files."""
    ours = [p.relative_to(root).as_posix() for p in root.glob("*/llms.txt")] + [GUIDES_INDEX, "directory.md"]
    return {RAW + path for path in ours} | {RAW + g.path for g in guides}


def check_all(root: Path = ROOT) -> list[str]:
    guides, errors = local_guides(root)
    data, schema = load_json(root / "catalog.json"), load_json(root / "catalog.schema.json")
    return errors + check_catalog(data, schema, reserved_fetch_urls(root, guides))
