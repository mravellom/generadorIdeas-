import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app
from app.models.idea import Idea
from app.models.analysis import Analysis
from app.models.execution import Execution  # noqa: F401

# Single in-memory SQLite shared across all connections
engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSession = sessionmaker(bind=engine)


@pytest.fixture(autouse=True)
def setup_db():
    """Create tables before each test, drop after."""
    Base.metadata.create_all(bind=engine)
    session = TestSession()

    # Override FastAPI's get_db to use the SAME session
    def _override():
        try:
            yield session
        finally:
            pass

    app.dependency_overrides[get_db] = _override
    yield session
    session.close()
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db(setup_db):
    """Return the shared test session."""
    return setup_db


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def sample_idea(db):
    idea = Idea(
        name="TestStartup",
        description="A failed test startup",
        failure_reason="Bad timing",
        industry="SaaS",
        year=2020,
        source_url="https://example.com/test",
    )
    db.add(idea)
    db.commit()
    db.refresh(idea)
    return idea


@pytest.fixture
def analyzed_idea(db, sample_idea):
    analysis = Analysis(
        idea_id=sample_idea.id,
        problem="Testing problem",
        failure_type="timing",
        current_opportunity="alta",
        pain_score=4,
        paying_capacity=3,
        mvp_ease=5,
        tech_advantage=4,
        total_score=16,
    )
    db.add(analysis)
    db.commit()
    db.refresh(sample_idea)
    return sample_idea
