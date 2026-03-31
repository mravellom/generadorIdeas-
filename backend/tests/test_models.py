"""Tests for SQLAlchemy models and their relationships."""
from app.models.idea import Idea
from app.models.analysis import Analysis
from app.models.execution import Execution


class TestIdeaModel:
    def test_create_idea(self, db):
        idea = Idea(name="Foo", description="Bar")
        db.add(idea)
        db.commit()
        assert idea.id is not None
        assert idea.name == "Foo"

    def test_optional_fields_default_none(self, db):
        idea = Idea(name="X", description="Y")
        db.add(idea)
        db.commit()
        assert idea.failure_reason is None
        assert idea.industry is None
        assert idea.year is None
        assert idea.source_url is None


class TestAnalysisRelationship:
    def test_idea_analysis_relationship(self, db, sample_idea):
        analysis = Analysis(
            idea_id=sample_idea.id,
            problem="test",
            failure_type="timing",
            current_opportunity="alta",
            pain_score=3,
            paying_capacity=3,
            mvp_ease=3,
            tech_advantage=3,
            total_score=12,
        )
        db.add(analysis)
        db.commit()
        db.refresh(sample_idea)
        assert sample_idea.analysis is not None
        assert sample_idea.analysis.total_score == 12

    def test_analysis_back_populates_idea(self, db, sample_idea):
        analysis = Analysis(idea_id=sample_idea.id, problem="p", total_score=5)
        db.add(analysis)
        db.commit()
        db.refresh(analysis)
        assert analysis.idea.name == "TestStartup"


class TestExecutionRelationship:
    def test_idea_execution_relationship(self, db, analyzed_idea):
        execution = Execution(
            idea_id=analyzed_idea.id,
            mvp_plan="Step 1",
            stack="Python",
            monetization="SaaS",
            estimated_days=3,
            status="pending",
        )
        db.add(execution)
        db.commit()
        db.refresh(analyzed_idea)
        assert analyzed_idea.execution is not None
        assert analyzed_idea.execution.estimated_days == 3

    def test_execution_default_status(self, db, sample_idea):
        execution = Execution(idea_id=sample_idea.id)
        db.add(execution)
        db.commit()
        assert execution.status == "pending"
