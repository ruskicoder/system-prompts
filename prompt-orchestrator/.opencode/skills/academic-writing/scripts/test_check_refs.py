#!/usr/bin/env python3
"""Self-tests for check_refs.py. No network: Crossref and HTTP calls are replaced by fakes.
Run: python3 -B -m unittest discover -s <this dir> -v"""
import io
import sys
import unittest
import urllib.error
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_refs  # noqa: E402
from check_refs import NO_IDENTIFIER, check_line, identifiers, reference_lines, url_status  # noqa: E402

LIANG = ('W. Liang, M. Yuksekgonul, Y. Mao, E. Wu, and J. Zou, "GPT detectors are biased against '
         'non-native English writers," Patterns, vol. 4, no. 7, 2023, doi: 10.1016/j.patter.2023.100779.')


def crossref(records):
    """Fake Crossref fetch: records maps DOI to (title, family name, year); others answer 404."""
    calls = []

    def fetch(url, timeout):
        doi = check_refs.urllib.parse.unquote(url.rsplit("/works/", 1)[1])
        calls.append(doi)
        if doi not in records:
            raise urllib.error.HTTPError(url, 404, "Not Found", {}, io.BytesIO())
        title, family, year = records[doi]
        return {"message": {"title": [title], "author": [{"family": family}],
                            "issued": {"date-parts": [[year]]}, "container-title": ["J"]}}
    fetch.calls = calls
    return fetch


def http(codes):
    """Fake URL status: codes maps each URL to the HTTP status it answers."""
    calls = []

    def status(url, timeout):
        calls.append(url)
        code = codes[url]
        return {"http": code, "browser_ua": False}
    status.calls = calls
    return status


class Resp:
    def __init__(self, status):
        self.status = status

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


class CheckRefsTests(unittest.TestCase):
    def test_reference_without_identifier_is_reported(self):
        res = check_line("[4] G. D. Gopen and J. A. Swan, \"The science of scientific writing,\" 1990.",
                         0.6, 1, crossref({}), http({}))
        self.assertEqual(res["status"], "unchecked")
        self.assertEqual(res["reason"], NO_IDENTIFIER)

    def test_every_doi_and_url_on_a_line_is_checked(self):
        line = ("[1] A. Author, \"Real title,\" 2023, doi: 10.1000/good. Data: doi:10.1000/missing. "
                "Code: https://example.org/repo and https://example.org/gone")
        fetch = crossref({"10.1000/good": ("Real title", "Author", 2023)})
        status = http({"https://example.org/repo": 200, "https://example.org/gone": 404})
        res = check_line(line, 0.6, 1, fetch, status)
        self.assertEqual(fetch.calls, ["10.1000/good", "10.1000/missing"])
        self.assertEqual(status.calls, ["https://example.org/repo", "https://example.org/gone"])
        self.assertEqual([c["status"] for c in res["checks"]], ["ok", "fail", "ok", "fail"])
        self.assertEqual(res["status"], "fail")

    def test_url_checked_when_line_also_has_doi(self):
        line = LIANG + " Available: https://www.cell.com/patterns/fulltext/S2666-3899(23)00130-7"
        fetch = crossref({"10.1016/j.patter.2023.100779": (
            "GPT detectors are biased against non-native English writers", "Liang", 2023)})
        status = http({"https://www.cell.com/patterns/fulltext/S2666-3899(23)00130-7": 200})
        res = check_line(line, 0.6, 1, fetch, status)
        self.assertEqual(len(status.calls), 1)
        self.assertEqual(res["status"], "ok")

    def test_doi_link_counts_as_the_doi_once(self):
        dois, urls = identifiers("Liang 2023. https://doi.org/10.1016/j.patter.2023.100779 "
                                 "doi:10.1016/j.patter.2023.100779")
        self.assertEqual(dois, ["10.1016/j.patter.2023.100779"])
        self.assertEqual(urls, [])

    def test_doi_with_brackets_stays_whole(self):
        sici = "10.1002/(SICI)1097-4571(199806)49:8<693::AID-ASI4>3.0.CO;2-O"
        dois, _ = identifiers(f"[2] B. Author, \"Old paper,\" 1998, doi: {sici}.")
        self.assertEqual(dois, [sici])
        dois, _ = identifiers("(see doi:10.1000/xyz123)")
        self.assertEqual(dois, ["10.1000/xyz123"])
        _, urls = identifiers("[Wiki](https://en.wikipedia.org/wiki/Mesh_(networking))")
        self.assertEqual(urls, ["https://en.wikipedia.org/wiki/Mesh_(networking)"])

    def test_title_compared_after_html_unescape(self):
        line = '[3] C. Lee, "Search & rescue with LoRa," 2024, doi: 10.1000/amp.'
        fetch = crossref({"10.1000/amp": ("Search &amp; rescue with <i>LoRa</i>", "Lee", 2024)})
        res = check_line(line, 0.99, 1, fetch, http({}))
        self.assertEqual(res["checks"][0]["crossref"]["title"], "Search & rescue with <i>LoRa</i>")
        self.assertEqual(res["status"], "ok", res)

    def test_title_mismatch_still_caught(self):
        fetch = crossref({"10.1016/j.patter.2023.100779": ("An unrelated study of soil", "Liang", 2023)})
        self.assertEqual(check_line(LIANG, 0.6, 1, fetch, http({}))["status"], "mismatch")

    def test_403_and_404_retried_with_browser_user_agent(self):
        for code in (403, 404):
            seen = []

            def opener(req, timeout, code=code):
                seen.append((req.get_method(), req.get_header("User-agent")))
                if req.get_header("User-agent") == check_refs.BROWSER_UA:
                    return Resp(200)
                raise urllib.error.HTTPError(req.full_url, code, "no", {}, io.BytesIO())
            res = url_status("https://example.org/paper", 1, opener)
            self.assertEqual(res, {"http": 200, "browser_ua": True})
            self.assertEqual(seen[-1], ("GET", check_refs.BROWSER_UA))

    def test_url_fails_when_browser_retry_also_fails(self):
        def opener(req, timeout):
            raise urllib.error.HTTPError(req.full_url, 404, "no", {}, io.BytesIO())
        self.assertEqual(url_status("https://example.org/x", 1, opener)["http"], 404)

    def test_server_error_not_retried(self):
        seen = []

        def opener(req, timeout):
            seen.append(req.get_method())
            raise urllib.error.HTTPError(req.full_url, 500, "no", {}, io.BytesIO())
        self.assertEqual(url_status("https://example.org/x", 1, opener)["http"], 500)
        self.assertEqual(seen, ["HEAD"])

    def test_reference_section_only(self):
        text = ("# Scope\n\nPrior work shows a 40 % drop [1].\n\n## 5. References\n\n"
                "[1] A, \"T,\" 2024.\n[2] B, \"U,\" 2023, doi: 10.1000/x.\n\n# Appendix\n\nNot a ref.\n")
        self.assertEqual(reference_lines(text), ['[1] A, "T," 2024.', '[2] B, "U," 2023, doi: 10.1000/x.'])
        self.assertEqual(reference_lines("[1] A.\n\n```\ncode\n```\n[2] B.\n"), ["[1] A.", "[2] B."])


if __name__ == "__main__":
    unittest.main()
