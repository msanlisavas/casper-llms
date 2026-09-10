import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import validate  # noqa: E402

SKILL = "---\nname: casper\ndescription: Answer Casper Network questions correctly.\n---\n\n# Casper\n"


class PluginTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.root)

    def write(self, path, content):
        file = self.root / path
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(content if isinstance(content, str) else json.dumps(content), encoding="utf-8")

    def market(self, *plugins):
        self.write(".claude-plugin/marketplace.json",
                   {"name": "casper-llms", "owner": {"name": "msanlisavas"}, "plugins": list(plugins)})

    def good(self):
        self.market({"name": "casper", "source": "./plugins/casper"},
                    {"name": "trade", "source": "./plugins/trade"},
                    {"name": "odra-plugin", "source": {"source": "git-subdir",
                                                       "url": "https://github.com/odradev/odradev-plugins.git",
                                                       "path": "plugins/odra-plugin"}})
        self.write("plugins/casper/.claude-plugin/plugin.json", {"name": "casper"})
        self.write("plugins/casper/skills/casper/SKILL.md", SKILL)
        self.write("plugins/trade/.claude-plugin/plugin.json", {"name": "trade"})
        self.write("plugins/trade/.mcp.json", {"mcpServers": {"trade": {
            "type": "http", "url": "https://mcp.example.org/mcp", "headers": {"X-Api-Key": "${EXAMPLE_API_KEY}"}}}})

    def errors(self):
        return " | ".join(validate.check_plugins(self.root))

    def test_a_well_formed_marketplace_passes(self):
        self.good()
        self.assertEqual(self.errors(), "")

    def test_a_literal_header_value_is_refused(self):
        self.good()
        self.write("plugins/trade/.mcp.json", {"mcpServers": {"trade": {
            "type": "http", "url": "https://mcp.example.org/mcp", "headers": {"X-Api-Key": "abc123"}}}})
        self.assertIn("environment variable", self.errors())

    def test_a_plain_http_server_url_is_refused(self):
        self.good()
        self.write("plugins/trade/.mcp.json", {"mcpServers": {"trade": {"type": "http", "url": "http://mcp.example.org/mcp"}}})
        self.assertIn("url must be https", self.errors())

    def test_the_plugin_name_must_match_its_manifest(self):
        self.good()
        self.write("plugins/casper/.claude-plugin/plugin.json", {"name": "other"})
        self.assertIn("differs from the marketplace entry", self.errors())

    def test_a_skill_name_must_match_its_folder(self):
        self.good()
        self.write("plugins/casper/skills/casper/SKILL.md", SKILL.replace("name: casper", "name: cspr"))
        self.assertIn("must match its folder", self.errors())

    def test_a_skill_needs_a_description(self):
        self.good()
        self.write("plugins/casper/skills/casper/SKILL.md", "---\nname: casper\n---\n# Casper\n")
        self.assertIn("description is required", self.errors())

    def test_a_missing_source_folder_is_refused(self):
        self.good()
        self.market({"name": "ghost", "source": "./plugins/ghost"})
        self.assertIn("not a folder in this repository", self.errors())

    def test_a_source_outside_the_repository_is_refused(self):
        self.good()
        outside = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, outside)
        (outside / ".claude-plugin").mkdir()
        (outside / ".claude-plugin" / "plugin.json").write_text('{"name": "casper"}', encoding="utf-8")
        self.market({"name": "casper", "source": "./" + Path("..", outside.name).as_posix()})
        self.assertIn("not a folder in this repository", self.errors())

    def test_an_unknown_external_source_type_is_refused(self):
        self.good()
        self.market({"name": "x", "source": {"source": "npm", "package": "x"}})
        self.assertIn("source type", self.errors())

    def test_no_marketplace_is_not_an_error(self):
        self.assertEqual(self.errors(), "")

    def test_the_shipped_marketplace_passes(self):
        self.assertEqual(validate.check_plugins(validate.ROOT), [])


if __name__ == "__main__":
    unittest.main()
