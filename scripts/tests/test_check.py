import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import catalog  # noqa: E402
import check  # noqa: E402

MCP = {"id": "m", "name": "M", "kind": "mcp-server", "url": "https://mcp.example.org/mcp",
       "docs": {"fetch": "https://example.org/m.md", "cite": "https://example.org/m"},
       "hosting": "hosted", "transport": ["streamable-http"], "auth": ["api-key"], "pricing": "free"}


def ok_get(url, api=False):
    return 200, "text/plain", ""


def ok_fetch(url):
    return "# page\n" + "x" * 400, ""


def refuse_post(url, body):
    raise AssertionError(f"no MCP request expected, got one to {url}")


class ProbeTests(unittest.TestCase):
    def test_an_mcp_server_that_answers_initialize_is_alive(self):
        post = lambda url, body: (200, "text/event-stream", 'data: {"jsonrpc":"2.0","id":1,"result":{}}')  # noqa: E731
        self.assertIsNone(check.probe_mcp("https://mcp.example.org/mcp", post))

    def test_an_mcp_server_that_wants_credentials_or_payment_is_alive(self):
        for status in (401, 402, 403):
            self.assertIsNone(check.probe_mcp("https://x/mcp", lambda url, body, s=status: (s, "", "")))

    def test_a_200_that_is_not_json_rpc_is_reported(self):
        problem = check.probe_mcp("https://x/mcp", lambda url, body: (200, "text/html", "<html>"))
        self.assertIn("HTTP 200", problem)

    def test_an_mcp_endpoint_that_404s_is_reported(self):
        self.assertIn("HTTP 404", check.probe_mcp("https://x/mcp", lambda url, body: (404, "text/html", "")))

    def test_an_unreachable_endpoint_is_reported(self):
        self.assertIn("unreachable", check.probe_mcp("https://x/mcp", lambda url, body: (0, "", "timed out")))

    def test_unreadable_docs_are_reported(self):
        post = lambda url, body: (401, "", "")  # noqa: E731
        problems = check.probe_entry(MCP, ok_get, post, lambda url: (None, "HTTP 404"))
        self.assertTrue(any("HTTP 404" in p for p in problems))

    def test_a_missing_documentation_page_is_reported(self):
        get = lambda url, api=False: (404, "", "") if url == MCP["docs"]["cite"] else (200, "", "")  # noqa: E731
        problems = check.probe_entry(MCP, get, lambda url, body: (401, "", ""), ok_fetch)
        self.assertTrue(any("documentation page" in p for p in problems))

    def test_an_sdk_is_checked_on_its_registry_api(self):
        seen = []
        get = lambda url, api=False: (seen.append(url), (200, "", ""))[1]  # noqa: E731
        sdk = dict(MCP, kind="sdk", url="https://www.nuget.org/packages/CSPR.Cloud.Net")
        self.assertEqual(check.probe_entry(sdk, get, refuse_post, ok_fetch), [])
        self.assertIn("https://api.nuget.org/v3-flatcontainer/cspr.cloud.net/index.json", seen)

    def test_a_self_hosted_server_is_checked_by_its_repository_not_probed(self):
        get = lambda url, api=False: (200, "", '{"archived": true}') if "api.github.com" in url else (200, "", "")  # noqa: E731
        self_hosted = dict(MCP, hosting="self-hosted", transport=["stdio", "streamable-http"],
                           url="https://github.com/example/server", source="https://github.com/example/server")
        self.assertIn("repository is archived", check.probe_entry(self_hosted, get, refuse_post, ok_fetch))

    def test_a_self_hosted_package_without_a_repository_is_checked_on_its_registry(self):
        seen = []
        get = lambda url, api=False: (seen.append(url), (200, "", ""))[1]  # noqa: E731
        package = dict(MCP, hosting="self-hosted", transport=["stdio"], url="https://www.npmjs.com/package/example-mcp")
        self.assertEqual(check.probe_entry(package, get, refuse_post, ok_fetch), [])
        self.assertIn("https://registry.npmjs.org/example-mcp", seen)
        self.assertNotIn("https://www.npmjs.com/package/example-mcp", seen)

    def test_a_skill_repository_is_checked_as_a_repository_not_read_as_markdown(self):
        skills = dict(MCP, kind="agent-skill", url="https://github.com/example/skills")
        fetched = []

        def fetch(url):
            fetched.append(url)
            return ok_fetch(url)

        get = lambda url, api=False: (200, "", '{"archived": false}')  # noqa: E731
        self.assertEqual(check.probe_entry(skills, get, refuse_post, fetch), [])
        self.assertNotIn("https://github.com/example/skills", fetched)

    def test_an_api_that_answers_below_500_is_alive(self):
        api = dict(MCP, kind="api", url="https://api.example.org")
        get = lambda url, api=False: (404, "", "") if url == "https://api.example.org" else (200, "", "")  # noqa: E731
        self.assertEqual(check.probe_entry(api, get, refuse_post, ok_fetch), [])


class StaleGuideTests(unittest.TestCase):
    GUIDE = catalog.Guide("guides/a.md", "A", "Verified against casper-node v2.2.2 on 2026-09-10.",
                          {"casper-node": "v2.2.2"})

    def test_a_newer_release_makes_a_guide_stale(self):
        self.assertEqual(check.stale_guides([self.GUIDE], {"casper-node": "v2.3.0"}),
                         ["guides/a.md: verified against casper-node v2.2.2; the latest is v2.3.0"])

    def test_the_same_release_with_or_without_v_is_current(self):
        self.assertEqual(check.stale_guides([self.GUIDE], {"casper-node": "2.2.2"}), [])

    def test_every_component_has_a_latest_lookup(self):
        self.assertEqual(set(check.LATEST), set(catalog.COMPONENTS))


if __name__ == "__main__":
    unittest.main()
