import json

from google import genai
from sqlalchemy.orm import Session

from app.config import settings
from app.models.analysis import Analysis
from app.models.idea import Idea

PROMPT = """Analiza esta startup fallida y responde SOLO con JSON válido (sin markdown, sin ```):

Nombre: {name}
Descripción: {description}
Razón de fallo: {failure_reason}
Industria: {industry}
Año: {year}

Responde con este formato exacto:
{{
  "problem": "el problema real que intentaban resolver",
  "failure_type": "timing|technology|execution|market",
  "current_opportunity": "alta|media|baja",
  "pain_score": 1-5,
  "paying_capacity": 1-5,
  "mvp_ease": 1-5,
  "tech_advantage": 1-5
}}

Criterios:
- pain_score: qué tan doloroso es el problema hoy (5 = muy doloroso)
- paying_capacity: la gente pagaría por resolverlo (5 = definitivamente)
- mvp_ease: qué tan fácil es hacer un MVP funcional (5 = un fin de semana)
- tech_advantage: la tecnología actual lo hace más viable (5 = mucho más viable)
"""


def analyze_idea(idea: Idea, db: Session) -> Analysis:
    client = genai.Client(api_key=settings.gemini_api_key)

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=PROMPT.format(
            name=idea.name,
            description=idea.description,
            failure_reason=idea.failure_reason or "No especificada",
            industry=idea.industry or "No especificada",
            year=idea.year or "No especificado",
        ),
    )

    data = json.loads(response.text)

    total = (
        data["pain_score"]
        + data["paying_capacity"]
        + data["mvp_ease"]
        + data["tech_advantage"]
    )

    existing = db.query(Analysis).filter(Analysis.idea_id == idea.id).first()
    if existing:
        for key, value in data.items():
            setattr(existing, key, value)
        existing.total_score = total
        analysis = existing
    else:
        analysis = Analysis(idea_id=idea.id, total_score=total, **data)
        db.add(analysis)

    db.commit()
    return analysis
