from sqlalchemy.orm import Session

from app.models.execution import Execution
from app.models.idea import Idea
from app.services.gemini import call_gemini

PROMPT = """Genera un plan de ejecución MVP para esta oportunidad. Responde SOLO con JSON válido (sin markdown, sin ```):

Idea original: {name}
Problema real: {problem}
Oportunidad actual: {opportunity}
Score: {score}/20

Responde con este formato exacto:
{{
  "mvp_plan": "Paso 1: ...\\nPaso 2: ...\\nPaso 3: ...",
  "stack": "backend: X, frontend: Y, db: Z",
  "monetization": "cómo monetizar este MVP",
  "estimated_days": 5
}}

El MVP debe ser construible en menos de 7 días por un solo desarrollador.
Sé concreto y práctico. Nada de fantasías.
"""


def generate_execution(idea: Idea, db: Session) -> Execution:
    data = call_gemini(
        PROMPT.format(
            name=idea.name,
            problem=idea.analysis.problem,
            opportunity=idea.analysis.current_opportunity,
            score=idea.analysis.total_score,
        )
    )

    days = data.get("estimated_days", 5)
    if isinstance(days, str):
        days = int(days.split("-")[0])
    data["estimated_days"] = days

    existing = db.query(Execution).filter(Execution.idea_id == idea.id).first()
    if existing:
        for key, value in data.items():
            setattr(existing, key, value)
        execution = existing
    else:
        execution = Execution(idea_id=idea.id, **data)
        db.add(execution)

    db.commit()
    return execution
