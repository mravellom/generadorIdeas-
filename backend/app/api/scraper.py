from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.scraper.startups_rip import scrape_startups_rip

router = APIRouter(prefix="/scraper", tags=["scraper"])


@router.post("/run")
def run_scraper(db: Session = Depends(get_db)):
    count = scrape_startups_rip(db)
    return {"message": f"Scraped {count} startups", "count": count}
