import json
import re

from playwright.sync_api import sync_playwright
from sqlalchemy.orm import Session

from app.models.idea import Idea


def _extract_companies(page_content: str) -> list[dict]:
    """Extract company data from Next.js RSC payloads."""
    unescaped = page_content.replace('\\"', '"').replace('\\\\', '\\')

    idx = unescaped.find('"companies":[{')
    if idx < 0:
        return []

    start = idx + len('"companies":')
    depth = 0
    end = start
    for i, c in enumerate(unescaped[start:], start):
        if c == '[':
            depth += 1
        elif c == ']':
            depth -= 1
        if depth == 0:
            end = i + 1
            break

    return json.loads(unescaped[start:end])


def scrape_startups_rip(db: Session) -> int:
    """Scrapes dead/acquired startups from startups.rip."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://startups.rip/", timeout=60000)
        page.wait_for_load_state("networkidle")

        # Get RSC payloads from script tags
        payloads = page.evaluate("""() => {
            const scripts = document.querySelectorAll('script');
            const results = [];
            for (const s of scripts) {
                if (s.textContent && s.textContent.includes('self.__next_f')) {
                    results.push(s.textContent);
                }
            }
            return results.join('\\n');
        }""")

        browser.close()

    companies = _extract_companies(payloads)

    count = 0
    for c in companies:
        name = c.get("name", "").strip()
        if not name:
            continue

        exists = db.query(Idea).filter(Idea.name == name).first()
        if exists:
            continue

        idea = Idea(
            name=name,
            description=c.get("oneLiner", ""),
            industry=c.get("category", ""),
            year=c.get("foundedYear"),
            source_url=f"https://startups.rip/{c.get('slug', '')}",
        )
        db.add(idea)
        count += 1

    db.commit()
    return count
