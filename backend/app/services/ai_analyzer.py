from sqlalchemy.orm import Session

from app.models.analysis import Analysis
from app.models.idea import Idea
from app.services.gemini import call_gemini

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
    data = call_gemini(
        PROMPT.format(
            name=idea.name,
            description=idea.description,
            failure_reason=idea.failure_reason or "No especificada",
            industry=idea.industry or "No especificada",
            year=idea.year or "No especificado",
        )
    )

    total = (
        data.get("pain_score", 0)
        + data.get("paying_capacity", 0)
        + data.get("mvp_ease", 0)
        + data.get("tech_advantage", 0)
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
