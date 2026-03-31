"""Tests for /api/ideas endpoints."""
from unittest.mock import patch


class TestListIdeas:
    def test_empty_list(self, client):
        resp = client.get("/api/ideas/")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_returns_ideas(self, client, sample_idea):
        resp = client.get("/api/ideas/")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["name"] == "TestStartup"


class TestGetIdea:
    def test_found(self, client, sample_idea):
        resp = client.get(f"/api/ideas/{sample_idea.id}")
        assert resp.status_code == 200
        assert resp.json()["name"] == "TestStartup"

    def test_not_found(self, client):
        resp = client.get("/api/ideas/999")
        assert resp.status_code == 404


class TestCreateIdea:
    def test_create(self, client):
        resp = client.post("/api/ideas/", json={
            "name": "NewIdea",
            "description": "A new idea",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "NewIdea"
        assert data["id"] is not None

    def test_create_with_all_fields(self, client):
        resp = client.post("/api/ideas/", json={
            "name": "Full",
            "description": "Desc",
            "failure_reason": "No market",
            "industry": "Fintech",
            "year": 2021,
            "source_url": "https://example.com",
        })
        assert resp.status_code == 200
        assert resp.json()["industry"] == "Fintech"


class TestTopOpportunities:
    def test_empty(self, client):
        resp = client.get("/api/ideas/top")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_returns_analyzed_sorted(self, client, analyzed_idea):
        resp = client.get("/api/ideas/top?limit=5")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["analysis"]["total_score"] == 16


class TestAnalyzeIdea:
    def test_not_found(self, client):
        resp = client.post("/api/ideas/999/analyze")
        assert resp.status_code == 404

    @patch("app.api.ideas.analyze_idea")
    def test_analyze_calls_service(self, mock_analyze, client, sample_idea):
        resp = client.post(f"/api/ideas/{sample_idea.id}/analyze")
        assert resp.status_code == 200
        mock_analyze.assert_called_once()


class TestExecuteIdea:
    def test_not_found(self, client):
        resp = client.post("/api/ideas/999/execute")
        assert resp.status_code == 404

    def test_requires_analysis(self, client, sample_idea):
        resp = client.post(f"/api/ideas/{sample_idea.id}/execute")
        assert resp.status_code == 400
        assert "Analyze" in resp.json()["detail"]

    @patch("app.api.ideas.generate_execution")
    def test_execute_calls_service(self, mock_exec, client, analyzed_idea):
        resp = client.post(f"/api/ideas/{analyzed_idea.id}/execute")
        assert resp.status_code == 200
        mock_exec.assert_called_once()


class TestBulkAnalyze:
    @patch("app.api.ideas.analyze_idea")
    def test_analyze_all_pending(self, mock_analyze, client, sample_idea):
        resp = client.post("/api/ideas/analyze-all")
        assert resp.status_code == 200
        data = resp.json()
        assert data["analyzed"] == 1
        assert data["errors"] == 0

    @patch("app.api.ideas.analyze_idea")
    def test_analyze_all_skips_analyzed(self, mock_analyze, client, analyzed_idea):
        resp = client.post("/api/ideas/analyze-all")
        assert resp.status_code == 200
        assert resp.json()["analyzed"] == 0
        mock_analyze.assert_not_called()

    @patch("app.api.ideas.analyze_idea", side_effect=RuntimeError("API down"))
    def test_analyze_all_counts_errors(self, mock_analyze, client, sample_idea):
        resp = client.post("/api/ideas/analyze-all")
        assert resp.status_code == 200
        data = resp.json()
        assert data["errors"] == 1
        assert data["analyzed"] == 0


class TestBulkExecute:
    @patch("app.api.ideas.generate_execution")
    def test_execute_all_pending(self, mock_exec, client, analyzed_idea):
        resp = client.post("/api/ideas/execute-all")
        assert resp.status_code == 200
        data = resp.json()
        assert data["executed"] == 1

    @patch("app.api.ideas.generate_execution")
    def test_execute_all_skips_unanalyzed(self, mock_exec, client, sample_idea):
        resp = client.post("/api/ideas/execute-all")
        assert resp.status_code == 200
        assert resp.json()["executed"] == 0
        mock_exec.assert_not_called()
