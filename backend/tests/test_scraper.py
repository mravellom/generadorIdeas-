"""Tests for the startups.rip scraper."""
import json
from unittest.mock import patch, MagicMock

from app.scraper.startups_rip import _extract_companies, scrape_startups_rip


class TestExtractCompanies:
    def test_extracts_valid_payload(self):
        payload = r'"companies":[{"name":"Foo","oneLiner":"Bar","category":"SaaS"}]'
        companies = _extract_companies(payload)
        assert len(companies) == 1
        assert companies[0]["name"] == "Foo"

    def test_returns_empty_on_no_match(self):
        assert _extract_companies("no data here") == []

    def test_handles_escaped_content(self):
        raw = r'\"companies\":[{\"name\":\"Test\",\"oneLiner\":\"Desc\"}]'
        companies = _extract_companies(raw)
        assert len(companies) == 1
        assert companies[0]["name"] == "Test"

    def test_handles_multiple_companies(self):
        data = json.dumps([
            {"name": "A", "oneLiner": "a"},
            {"name": "B", "oneLiner": "b"},
        ])
        payload = f'"companies":{data}'
        companies = _extract_companies(payload)
        assert len(companies) == 2

    def test_returns_empty_on_invalid_json(self):
        payload = '"companies":[{invalid json}]'
        assert _extract_companies(payload) == []


class TestScrapeStartupsRip:
    @patch("app.scraper.startups_rip.sync_playwright")
    def test_saves_new_ideas(self, mock_pw, db):
        # Build mock playwright chain
        mock_page = MagicMock()
        mock_browser = MagicMock()
        mock_browser.new_page.return_value = mock_page
        mock_p = MagicMock()
        mock_p.chromium.launch.return_value = mock_browser
        mock_pw.return_value.__enter__ = MagicMock(return_value=mock_p)
        mock_pw.return_value.__exit__ = MagicMock(return_value=False)

        companies = [{"name": "StartupA", "oneLiner": "Desc A", "category": "AI", "slug": "startup-a"}]
        payload = r'"companies":' + json.dumps(companies)
        # evaluate is called multiple times: scrolls + payload extraction
        mock_page.evaluate.side_effect = [
            None,   # first scroll
            100,    # first height check
            None,   # second scroll
            100,    # second height check (same = stop)
            payload  # RSC payload extraction
        ]

        count = scrape_startups_rip(db)
        assert count == 1

    @patch("app.scraper.startups_rip.sync_playwright")
    def test_skips_duplicates(self, mock_pw, db):
        from app.models.idea import Idea
        db.add(Idea(name="Existing", description="Already here"))
        db.commit()

        mock_page = MagicMock()
        mock_browser = MagicMock()
        mock_browser.new_page.return_value = mock_page
        mock_p = MagicMock()
        mock_p.chromium.launch.return_value = mock_browser
        mock_pw.return_value.__enter__ = MagicMock(return_value=mock_p)
        mock_pw.return_value.__exit__ = MagicMock(return_value=False)

        companies = [{"name": "Existing", "oneLiner": "Dup", "slug": "existing"}]
        payload = r'"companies":' + json.dumps(companies)
        mock_page.evaluate.side_effect = [None, 100, None, 100, payload]

        count = scrape_startups_rip(db)
        assert count == 0

    @patch("app.scraper.startups_rip.sync_playwright", side_effect=Exception("Browser crash"))
    def test_returns_zero_on_error(self, mock_pw, db):
        count = scrape_startups_rip(db)
        assert count == 0
