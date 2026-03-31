"""Tests for AI services: gemini helper, analyzer, execution generator."""
import json
from unittest.mock import patch, MagicMock

import pytest

from app.services.gemini import _clean_json, call_gemini


class TestCleanJson:
    def test_plain_json(self):
        assert _clean_json('{"a": 1}') == '{"a": 1}'

    def test_strips_code_fences(self):
        raw = '```json\n{"a": 1}\n```'
        assert _clean_json(raw) == '{"a": 1}'

    def test_strips_fences_no_lang(self):
        raw = '```\n{"a": 1}\n```'
        assert _clean_json(raw) == '{"a": 1}'

    def test_strips_whitespace(self):
        assert _clean_json('  {"a": 1}  ') == '{"a": 1}'


class TestCallGemini:
    @patch("app.services.gemini._get_client")
    def test_success(self, mock_client):
        mock_resp = MagicMock()
        mock_resp.text = '{"key": "value"}'
        mock_client.return_value.models.generate_content.return_value = mock_resp

        result = call_gemini("test prompt")
        assert result == {"key": "value"}

    @patch("app.services.gemini._get_client")
    def test_cleans_markdown_fences(self, mock_client):
        mock_resp = MagicMock()
        mock_resp.text = '```json\n{"key": "value"}\n```'
        mock_client.return_value.models.generate_content.return_value = mock_resp

        result = call_gemini("test prompt")
        assert result == {"key": "value"}

    @patch("app.services.gemini._get_client")
    def test_retries_on_invalid_json(self, mock_client):
        bad_resp = MagicMock()
        bad_resp.text = "not json"
        good_resp = MagicMock()
        good_resp.text = '{"ok": true}'
        mock_client.return_value.models.generate_content.side_effect = [bad_resp, good_resp]

        result = call_gemini("test", max_retries=2)
        assert result == {"ok": True}

    @patch("app.services.gemini._get_client")
    def test_raises_after_max_retries(self, mock_client):
        bad_resp = MagicMock()
        bad_resp.text = "not json"
        mock_client.return_value.models.generate_content.return_value = bad_resp

        with pytest.raises(RuntimeError, match="failed after 2 attempts"):
            call_gemini("test", max_retries=2)


class TestAnalyzeIdea:
    @patch("app.services.ai_analyzer.call_gemini")
    def test_creates_analysis(self, mock_gemini, db, sample_idea):
        mock_gemini.return_value = {
            "problem": "No market fit",
            "failure_type": "market",
            "current_opportunity": "alta",
            "pain_score": 4,
            "paying_capacity": 3,
            "mvp_ease": 5,
            "tech_advantage": 4,
        }
        from app.services.ai_analyzer import analyze_idea
        analysis = analyze_idea(sample_idea, db)
        assert analysis.total_score == 16
        assert analysis.problem == "No market fit"
        assert analysis.idea_id == sample_idea.id

    @patch("app.services.ai_analyzer.call_gemini")
    def test_updates_existing_analysis(self, mock_gemini, db, analyzed_idea):
        mock_gemini.return_value = {
            "problem": "Updated",
            "failure_type": "timing",
            "current_opportunity": "baja",
            "pain_score": 1,
            "paying_capacity": 1,
            "mvp_ease": 1,
            "tech_advantage": 1,
        }
        from app.services.ai_analyzer import analyze_idea
        analysis = analyze_idea(analyzed_idea, db)
        assert analysis.total_score == 4
        assert analysis.problem == "Updated"


class TestGenerateExecution:
    @patch("app.services.execution_generator.call_gemini")
    def test_creates_execution(self, mock_gemini, db, analyzed_idea):
        mock_gemini.return_value = {
            "mvp_plan": "Step 1: Build",
            "stack": "Python, React",
            "monetization": "Subscriptions",
            "estimated_days": 5,
        }
        from app.services.execution_generator import generate_execution
        execution = generate_execution(analyzed_idea, db)
        assert execution.estimated_days == 5
        assert execution.mvp_plan == "Step 1: Build"
        assert execution.idea_id == analyzed_idea.id

    @patch("app.services.execution_generator.call_gemini")
    def test_handles_string_days(self, mock_gemini, db, analyzed_idea):
        mock_gemini.return_value = {
            "mvp_plan": "Plan",
            "stack": "Node",
            "monetization": "Ads",
            "estimated_days": "3-5",
        }
        from app.services.execution_generator import generate_execution
        execution = generate_execution(analyzed_idea, db)
        assert execution.estimated_days == 3
