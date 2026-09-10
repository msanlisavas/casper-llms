import json
import re
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import catalog  # noqa: E402
import validate  # noqa: E402

SCHEMA = catalog.load_json(catalog.ROOT / "catalog.schema.json")


def entry(**changes):
    base = {
        "id": "example-mcp", "name": "Example MCP server", "kind": "mcp-server",
        "publisher": {"name": "Example", "url": "https://example.org"},
        "description": "Reads Casper accounts and blocks for an agent.",
        "url": "https://mcp.example.org/mcp",
        "docs": {"fetch": "https://example.org/mcp.md", "cite": "https://example.org/mcp"},
        "hosting": "hosted", "transport": ["streamable-http"], "auth": ["none"], "pricing": "free",
    }
    base.update(changes)
    return {key: value for key, value in base.items() if value is not None}


def errors_for(*entries, reserved=frozenset()):
    return " | ".join(catalog.check_catalog({"capabilities": list(entries)}, SCHEMA, set(reserved)))


class SchemaTests(unittest.TestCase):
    def test_a_complete_entry_passes(self):
        self.assertEqual(errors_for(entry()), "")

    def test_a_missing_required_field_fails(self):
        self.assertIn("missing required field 'pricing'", errors_for(entry(pricing=None)))

    def test_an_unknown_field_fails(self):
        self.assertIn("unknown field 'homepage'", errors_for(entry(homepage="https://example.org")))

    def test_an_mcp_server_must_say_how_to_connect(self):
        self.assertIn("missing required field 'transport'", errors_for(entry(transport=None)))
        self.assertIn("missing required field 'hosting'", errors_for(entry(hosting=None)))

    def test_a_paid_capability_must_say_what_it_costs(self):
        self.assertIn("pricingNote", errors_for(entry(pricing="paid")))
        self.assertEqual(errors_for(entry(pricing="paid", pricingNote="0.02 USD per query")), "")

    def test_urls_must_be_https(self):
        self.assertIn("does not match", errors_for(entry(url="http://mcp.example.org/mcp")))

    def test_a_long_description_fails(self):
        self.assertIn("longer than 300", errors_for(entry(description="x" * 301)))

    def test_a_pipe_in_a_name_fails_because_it_breaks_the_readme_table(self):
        self.assertIn("does not match", errors_for(entry(name="A | B")))

    def test_ours_may_only_be_true(self):
        self.assertIn("must be True", errors_for(entry(ours=False)))

    def test_an_unsupported_schema_keyword_is_refused(self):
        with self.assertRaises(ValueError):
            catalog.schema_errors("x", {"type": "string", "format": "uri"}, {}, "t")

    def test_the_shipped_catalog_is_valid(self):
        self.assertEqual(catalog.check_all(catalog.ROOT), [])


class CrossEntryTests(unittest.TestCase):
    def test_ids_are_unique(self):
        second = entry(docs={"fetch": "https://example.org/b.md", "cite": "https://example.org/b"})
        self.assertIn("id is used twice", errors_for(entry(), second))

    def test_a_fetch_url_is_listed_once(self):
        self.assertIn("already listed", errors_for(entry(), entry(id="other")))

    def test_a_fetch_url_this_repository_lists_is_reserved(self):
        self.assertIn("already listed", errors_for(entry(), reserved={"https://example.org/mcp.md"}))

    def test_an_llms_txt_entry_is_its_own_documentation(self):
        docs = entry(id="docs", kind="llms-txt", url="https://example.org/llms.txt", transport=None, auth=None)
        self.assertIn("docs.fetch must equal url", errors_for(docs))


GOOD_GUIDE = ("# A guide\n\nVerified against casper-node v2.2.2 and docs.casper.network 2.0.0 on 2026-09-10.\n\n"
              "Body with a [source](https://github.com/casper-network/casper-node/blob/v2.2.2/README.md).\n")


class GuideTests(unittest.TestCase):
    def test_a_guide_names_what_it_was_verified_against(self):
        guide, errors = catalog.parse_guide("guides/a.md", GOOD_GUIDE)
        self.assertEqual(errors, [])
        self.assertEqual(guide.versions, {"casper-node": "v2.2.2", "docs.casper.network": "2.0.0"})
        self.assertEqual(guide.title, "A guide")

    def test_frontmatter_is_refused(self):
        _, errors = catalog.parse_guide("guides/a.md", "---\ntitle: A\n---\n" + GOOD_GUIDE)
        self.assertTrue(any("H1" in e for e in errors))

    def test_a_missing_verification_line_is_refused(self):
        _, errors = catalog.parse_guide("guides/a.md", "# A guide\n\nNo line here.\n")
        self.assertTrue(any("line 3" in e for e in errors))

    def test_a_component_the_weekly_check_cannot_follow_is_refused(self):
        text = GOOD_GUIDE.replace("casper-node v2.2.2", "casper-sidecar v1.0.0")
        _, errors = catalog.parse_guide("guides/a.md", text)
        self.assertTrue(any("casper-sidecar" in e for e in errors))

    def test_html_is_refused(self):
        _, errors = catalog.parse_guide("guides/a.md", GOOD_GUIDE + "<div>x</div>\n")
        self.assertTrue(any("HTML" in e for e in errors))


INDEX = ("# Casper docs\n\n> The docs, e.g. concepts. More text.\n\n## A\n\n"
         "- [Page](https://raw.githubusercontent.com/o/r/main/p.md): https://docs.example.org/p\n")


class RenderTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        self.write("catalog.schema.json", json.dumps(SCHEMA))
        llms = entry(id="example-docs", name="Example docs", kind="llms-txt", url="https://example.org/llms.txt",
                     docs={"fetch": "https://example.org/llms.txt", "cite": "https://example.org"},
                     transport=None, auth=None)
        self.write("catalog.json", json.dumps({"capabilities": [entry(), llms]}))
        self.write("README.md", "# x\n\n<!-- indexes:start -->\n<!-- indexes:end -->\n\n"
                                "<!-- catalog:start -->\nold\n<!-- catalog:end -->\n\n"
                                "<!-- guides:start -->\n<!-- guides:end -->\n")
        self.write("casper-docs/llms.txt", INDEX)
        self.write("guides/a.md", GOOD_GUIDE)

    def tearDown(self):
        shutil.rmtree(self.root)

    def write(self, path, text):
        (self.root / path).parent.mkdir(parents=True, exist_ok=True)
        (self.root / path).write_text(text, encoding="utf-8")

    def read(self, path):
        return (self.root / path).read_text(encoding="utf-8")

    def test_after_writing_nothing_is_stale(self):
        changed = catalog.write_all(self.root)
        self.assertEqual(set(changed), {"llms.txt", "directory.md", "README.md", "casper-guides/llms.txt"})
        self.assertEqual(catalog.stale_outputs(self.root), [])

    def test_editing_the_catalog_makes_the_renders_stale(self):
        catalog.write_all(self.root)
        self.write("catalog.json", json.dumps({"capabilities": [entry(name="Renamed server")]}))
        self.assertIn("llms.txt", catalog.stale_outputs(self.root))

    def test_the_root_index_obeys_the_ingester_grammar(self):
        catalog.write_all(self.root)
        text = self.read("llms.txt")
        self.assertEqual(validate.check_text(text, "llms.txt"), [])
        self.assertIn("## MCP servers", text)
        self.assertIn("Endpoint: https://mcp.example.org/mcp.", text)
        self.assertIn("[A guide](https://raw.githubusercontent.com/msanlisavas/casper-llms/main/guides/a.md)", text)
        self.assertIn("1 page. The docs, e.g. concepts.", text)

    def test_a_self_hosted_server_has_no_endpoint(self):
        self_hosted = entry(hosting="self-hosted", url="https://github.com/example/server")
        self.write("catalog.json", json.dumps({"capabilities": [self_hosted]}))
        catalog.write_all(self.root)
        self.assertNotIn("Endpoint", self.read("llms.txt"))
        self.assertIn("- **Hosting:** Self-hosted", self.read("directory.md"))

    def test_an_index_is_described_by_the_lead_of_its_summary(self):
        self.write("casper-docs/llms.txt", INDEX.replace("The docs, e.g. concepts. More text.",
                                                         "The node software: casper-client, the sidecar. More."))
        catalog.write_all(self.root)
        self.assertIn("1 page. The node software.", self.read("llms.txt"))

    def test_the_guides_index_obeys_the_grammar_and_the_root_lists_it(self):
        catalog.write_all(self.root)
        self.assertEqual(validate.check_text(self.read("casper-guides/llms.txt"), "casper-guides/llms.txt"), [])
        self.assertIn(catalog.RAW + "casper-guides/llms.txt", self.read("llms.txt"))

    def test_readme_links_land_on_directory_headings(self):
        catalog.write_all(self.root)
        used = {}
        anchors = [catalog.slug(h, used) for h in re.findall(r"^#{1,6} (.+)$", self.read("directory.md"), re.M)]
        links = re.findall(r"directory\.md#([\w-]+)", self.read("README.md"))
        self.assertTrue(links)
        for anchor in links:
            self.assertIn(anchor, anchors)

    def test_the_readme_index_table_counts_pages(self):
        catalog.write_all(self.root)
        self.assertIn("| [`casper-docs/llms.txt`](casper-docs/llms.txt) | 1 | The docs, e.g. concepts |", self.read("README.md"))
        self.assertIn("| [`casper-guides/llms.txt`](casper-guides/llms.txt) | 1 |", self.read("README.md"))

    def test_missing_readme_markers_fail_loudly(self):
        self.write("README.md", "# x\n")
        with self.assertRaises(ValueError):
            catalog.render_all(self.root)

    def test_slugs_match_github(self):
        used = {}
        self.assertEqual(catalog.slug("CSPR.cloud MCP server", used), "csprcloud-mcp-server")
        self.assertEqual(catalog.slug("CSPR.cloud MCP server", used), "csprcloud-mcp-server-1")


if __name__ == "__main__":
    unittest.main()
