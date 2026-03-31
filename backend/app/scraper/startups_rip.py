import json
import logging

from playwright.sync_api import sync_playwright
from sqlalchemy.orm import Session

from app.models.idea import Idea

logger = logging.getLogger(__name__)

MAX_SCROLLS = 30
SCROLL_PAUSE_MS = 2000


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

    try:
        return json.loads(unescaped[start:end])
    except json.JSONDecodeError:
        logger.error("Failed to parse companies JSON from page content")
        return []


def _scroll_to_load_all(page) -> None:
    """Scroll down repeatedly to trigger infinite-scroll loading."""
    prev_height = 0
    for i in range(MAX_SCROLLS):
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(SCROLL_PAUSE_MS)
        new_height = page.evaluate("document.body.scrollHeight")
        if new_height == prev_height:
            logger.info("Scroll stopped after %d iterations (no new content)", i + 1)
            break
        prev_height = new_height


def scrape_startups_rip(db: Session) -> int:
    """Scrapes dead/acquired startups from startups.rip."""
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto("https://startups.rip/", timeout=60000)
            page.wait_for_load_state("networkidle")

            _scroll_to_load_all(page)

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
    except Exception as e:
        logger.error("Scraper failed: %s", e)
        return 0

    companies = _extract_companies(payloads)
    logger.info("Extracted %d companies from startups.rip", len(companies))

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
            failure_reason=c.get("shutdownReason") or c.get("reason") or "",
            industry=c.get("category", ""),
            year=c.get("foundedYear"),
            source_url=f"https://startups.rip/{c.get('slug', '')}",
        )
        db.add(idea)
        count += 1

    db.commit()
    logger.info("Saved %d new ideas to database", count)
    return count
