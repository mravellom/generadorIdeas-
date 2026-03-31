"""Tests for /api/scraper endpoints."""
from unittest.mock import patch


class TestRunScraper:
    @patch("app.api.scraper.scrape_startups_rip", return_value=5)
    def test_run_returns_count(self, mock_scrape, client):
        resp = client.post("/api/scraper/run")
        assert resp.status_code == 200
        data = resp.json()
        assert data["count"] == 5
        assert "5" in data["message"]
        mock_scrape.assert_called_once()

    @patch("app.api.scraper.scrape_startups_rip", return_value=0)
    def test_run_zero_results(self, mock_scrape, client):
        resp = client.post("/api/scraper/run")
        assert resp.status_code == 200
        assert resp.json()["count"] == 0
