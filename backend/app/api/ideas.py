import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.analysis import Analysis
from app.models.execution import Execution
from app.models.idea import Idea
from app.schemas.idea import IdeaCreate, IdeaOut
from app.services.ai_analyzer import analyze_idea
from app.services.execution_generator import generate_execution

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/ideas", tags=["ideas"])


@router.get("/", response_model=list[IdeaOut])
def list_ideas(db: Session = Depends(get_db)):
    return db.query(Idea).all()


@router.get("/top", response_model=list[IdeaOut])
def top_opportunities(limit: int = 10, db: Session = Depends(get_db)):
    ideas = (
        db.query(Idea)
        .join(Analysis)
        .order_by(Analysis.total_score.desc())
        .limit(limit)
        .all()
    )
    return ideas


@router.get("/{idea_id}", response_model=IdeaOut)
def get_idea(idea_id: int, db: Session = Depends(get_db)):
    idea = db.query(Idea).filter(Idea.id == idea_id).first()
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    return idea


@router.post("/", response_model=IdeaOut)
def create_idea(idea_in: IdeaCreate, db: Session = Depends(get_db)):
    idea = Idea(**idea_in.model_dump())
    db.add(idea)
    db.commit()
    db.refresh(idea)
    return idea


@router.post("/{idea_id}/analyze", response_model=IdeaOut)
def analyze(idea_id: int, db: Session = Depends(get_db)):
    idea = db.query(Idea).filter(Idea.id == idea_id).first()
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    analyze_idea(idea, db)
    db.refresh(idea)
    return idea


@router.post("/{idea_id}/execute", response_model=IdeaOut)
def execute(idea_id: int, db: Session = Depends(get_db)):
    idea = db.query(Idea).filter(Idea.id == idea_id).first()
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    if not idea.analysis:
        raise HTTPException(status_code=400, detail="Analyze the idea first")
    generate_execution(idea, db)
    db.refresh(idea)
    return idea


@router.post("/analyze-all")
def analyze_all(db: Session = Depends(get_db)):
    """Analyze all ideas that don't have an analysis yet."""
    ideas = (
        db.query(Idea)
        .filter(~Idea.id.in_(db.query(Analysis.idea_id)))
        .all()
    )
    analyzed = 0
    errors = 0
    for idea in ideas:
        try:
            analyze_idea(idea, db)
            analyzed += 1
        except Exception as e:
            errors += 1
            logger.error("Failed to analyze idea %d (%s): %s", idea.id, idea.name, e)
    return {"analyzed": analyzed, "errors": errors, "pending": len(ideas) - analyzed - errors}


@router.post("/execute-all")
def execute_all(db: Session = Depends(get_db)):
    """Generate execution plans for all analyzed ideas without one."""
    ideas = (
        db.query(Idea)
        .join(Analysis)
        .filter(~Idea.id.in_(db.query(Execution.idea_id)))
        .all()
    )
    executed = 0
    errors = 0
    for idea in ideas:
        try:
            generate_execution(idea, db)
            executed += 1
        except Exception as e:
            errors += 1
            logger.error("Failed to generate execution for idea %d (%s): %s", idea.id, idea.name, e)
    return {"executed": executed, "errors": errors, "pending": len(ideas) - executed - errors}
