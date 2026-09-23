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


class RobustnessTests(unittest.TestCase):
    """Found by review: one misbehaving host must not take the whole weekly report down."""

    def test_a_probe_that_raises_becomes_a_finding(self):
        def boom(entry):
            raise ConnectionResetError("reset by peer")
        self.assertEqual(check.safe_probe(MCP, boom), ["probe failed: ConnectionResetError"])

    def test_a_version_lookup_that_exits_is_reported_not_fatal(self):
        def fails():
            raise SystemExit("latest release of casper-network/casper-node failed with HTTP 502")
        latest, problems = check.latest_versions({"casper-node"}, {"casper-node": fails})
        self.assertEqual(latest, {})
        self.assertIn("could not determine the latest casper-node", problems[0])

    def test_a_trickling_response_hits_the_deadline(self):
        import time

        class Trickle:    # a keep-alive every 20 ms: each read succeeds, the whole never ends
            def read1(self, n):
                time.sleep(0.02)
                return b": keep-alive\n"
        with self.assertRaises(TimeoutError):
            check.read_bounded(Trickle(), b'"jsonrpc"', seconds=0.1, cap=10**9)

    def test_a_folded_content_type_cannot_carry_markdown_into_the_issue(self):
        folded = "text/html\r\n \r\n ## Pwned [link](https://evil.example) @someone"
        problem = check.probe_mcp("https://x/mcp", lambda url, body: (500, folded, ""))
        self.assertNotIn("#", problem)
        self.assertNotIn("@", problem)
        self.assertIn("an unexpected content type", problem)
        self.assertEqual(check.media_type("text/html; charset=utf-8"), "text/html")

    def test_a_permanent_redirect_is_reported_as_a_move(self):
        problem = check.probe_mcp("https://x/mcp", lambda url, body: (301, "", "https://y.example/mcp"))
        self.assertIn("moved to `https://y.example/mcp`", problem)

    def test_a_307_keeps_the_post_and_its_body(self):
        import urllib.request
        req = urllib.request.Request("https://x/mcp", data=b"{}", method="POST", headers={"Content-Type": "application/json"})
        followed = check._McpRedirects().redirect_request(req, None, 307, "Temporary", {}, "https://y/mcp")
        self.assertEqual((followed.get_method(), followed.data, followed.full_url), ("POST", b"{}", "https://y/mcp"))

    def test_a_legacy_sse_server_is_probed_with_a_get(self):
        sse = dict(MCP, transport=["sse"], url="https://mcp.example.org/sse")
        stream = lambda url: (200, "text/event-stream", "event: endpoint\ndata: /messages?session=1\n")  # noqa: E731
        self.assertEqual(check.probe_entry(sse, ok_get, refuse_post, ok_fetch, stream), [])
        silent = lambda url: (200, "text/event-stream", ": keep-alive\n")  # noqa: E731
        self.assertTrue(check.probe_entry(sse, ok_get, refuse_post, ok_fetch, silent))

    def test_findings_and_a_clean_run_have_distinct_exit_codes(self):
        import tempfile
        saved = (check.safe_probe, catalog.load_json, catalog.local_guides)
        try:
            catalog.load_json = lambda path: {"capabilities": [MCP]}
            catalog.local_guides = lambda root=None: ([], [])
            report = Path(tempfile.mkdtemp()) / "report.md"
            check.safe_probe = lambda entry: ["down"]
            self.assertEqual(check.main(["--report", str(report)]), check.FINDINGS)
            self.assertIn("down", report.read_text(encoding="utf-8"))
            check.safe_probe = lambda entry: []
            self.assertEqual(check.main([]), 0)
        finally:
            check.safe_probe, catalog.load_json, catalog.local_guides = saved


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


SHELL = ('<!doctype html><html><head><meta name="description" content="Public testnet live, mainnet October 2026." />'
         '<script type="module" crossorigin src="/assets/index-DSzftkm_.js"></script></head>'
         '<body><div id="root"></div></body></html>')


class SiteShellTests(unittest.TestCase):
    """A website with no releases is versioned by the digest of the shell it serves."""

    def version(self, body, status=200, content_type="text/html"):
        return check.site_shell("https://site.example/", lambda url, api=False: (status, content_type, body))

    def test_the_version_is_the_digest_of_the_shell(self):
        import hashlib
        self.assertEqual(self.version(SHELL), "shell-" + hashlib.sha256(SHELL.encode("utf-8")).hexdigest()[:12])

    def test_a_redeploy_of_the_same_bytes_is_the_same_version(self):
        self.assertEqual(self.version(SHELL), self.version("".join(SHELL)))

    def test_a_new_bundle_moves_the_version(self):
        self.assertNotEqual(self.version(SHELL), self.version(SHELL.replace("DSzftkm_", "Ab3dE9_x")))

    def test_an_edit_to_the_meta_tags_alone_moves_the_version(self):
        self.assertNotEqual(self.version(SHELL), self.version(SHELL.replace("October", "November")))

    def test_a_shell_that_loads_a_runtime_config_first_is_still_a_shell(self):
        # testnet.astralbeam.io loads /config.<hash>.js before its entry bundle.
        body = SHELL.replace('<script type="module"', '<script src="/config.6b682550.js"></script><script type="module"')
        self.assertTrue(self.version(body).startswith("shell-"))

    def test_a_page_that_is_not_a_vite_shell_is_reported_not_compared(self):
        for args in ((SHELL, 404), (SHELL, 200, "text/plain"), ("<html><body>moved</body></html>",),
                     (SHELL.replace("index-DSzftkm_", "main"),)):
            with self.assertRaises(RuntimeError):
                self.version(*args)

    def test_a_site_lookup_that_fails_is_reported_not_fatal(self):
        def fails():
            raise RuntimeError("https://astralbeam.io/ answered HTTP 503 (text/html)")
        latest, problems = check.latest_versions({"astralbeam.io"}, {"astralbeam.io": fails})
        self.assertEqual(latest, {})
        self.assertIn("could not determine the latest astralbeam.io", problems[0])

    def test_a_guide_verified_against_an_older_shell_is_stale(self):
        guide = catalog.Guide("guides/astralbeam.md", "A", "Verified against astralbeam.io shell-0d177dc86bed on 2026-09-23.",
                              {"astralbeam.io": "shell-0d177dc86bed"})
        self.assertEqual(check.stale_guides([guide], {"astralbeam.io": "shell-0d177dc86bed"}), [])
        self.assertEqual(check.stale_guides([guide], {"astralbeam.io": "shell-9a1b2c3d4e5f"}),
                         ["guides/astralbeam.md: verified against astralbeam.io shell-0d177dc86bed; "
                          "the latest is shell-9a1b2c3d4e5f"])


class SitemapDateTests(unittest.TestCase):
    """A documentation site with no releases is versioned by the newest page edit in its sitemap."""

    def test_the_version_is_the_newest_lastmod(self):
        xml = ("<urlset><url><lastmod>2026-09-09T10:00:00Z</lastmod></url>"
               "<url><lastmod>2026-09-21T20:48:17.811Z</lastmod></url><url><lastmod>2026-08-11</lastmod></url></urlset>")
        self.assertEqual(check.sitemap_date("https://d/", lambda url, api=False: (200, "application/xml", xml)), "2026.09.21")

    def test_an_html_answer_or_an_empty_sitemap_is_reported(self):
        for status, content_type, body in ((200, "text/html", "<lastmod>2026-09-21</lastmod>"),
                                           (200, "application/xml", "<urlset/>"), (404, "application/xml", "")):
            with self.assertRaises(RuntimeError):
                check.sitemap_date("https://d/", lambda url, api=False: (status, content_type, body))


if __name__ == "__main__":
    unittest.main()
