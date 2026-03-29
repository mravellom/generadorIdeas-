from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.analysis import Analysis
from app.models.idea import Idea
from app.schemas.idea import IdeaCreate, IdeaOut
from app.services.ai_analyzer import analyze_idea
from app.services.execution_generator import generate_execution

router = APIRouter(prefix="/ideas", tags=["ideas"])


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
