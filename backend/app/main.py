from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import ideas, scraper

app = FastAPI(title="Opportunity Engine", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200", "http://localhost", "http://localhost:8004"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ideas.router)
app.include_router(scraper.router)


@app.get("/")
def root():
    return {"name": "Opportunity Engine", "status": "running"}
