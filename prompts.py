BASE_RULES = """
Eres un técnico de Contratación Pública. Redactas de manera administrativa, clara y conforme a la LCSP.
- Mantén referencias a la LCSP sólo cuando sean necesarias y no inventes artículos.
- Si el usuario ha indicado otra normativa, cítala con precisión.
- No repitas contenido ya aprobado en puntos anteriores; evita contradicciones.
- Devuelve texto directo para el punto solicitado, sin encabezados redundantes.
"""

CHECKLISTS = {
    "OBJETO": [
        "Denominación exacta del contrato (corta y larga)",
        "Unidad promotora/servicio",
        "Alcance: qué incluye / qué excluye",
        "Tipología (servicio/suministro/obra) y CPV previsto",
        "Usuarios finales o destinatarios",
        "Ámbito territorial",
        "¿Normativa adicional a LCSP que deba citarse? (adjuntar si aplica)"
    ],
    "NECESIDAD": [
        "Problema/Carencia actual que motiva el contrato",
        "Objetivos que se persiguen",
        "Consecuencias de no contratar",
        "Carácter periódico o puntual de la necesidad",
        "Datos/indicadores disponibles que justifiquen la necesidad"
    ],
    "INSUFICIENCIA_MEDIOS": [
        "Descripción de los medios propios existentes",
        "Por qué resultan insuficientes/inadecuados",
        "Intentos previos o informes internos (si los hay)",
        "Necesidad de recurrir a medios externos"
    ]
}

def build_prompt(point_name: str, answers: dict, approved_points: dict) -> str:
    resume_prev = []
    for k, v in approved_points.items():
        if v:
            resume_prev.append(f"[{k}] {v[:300]}{'...' if len(v)>300 else ''}")
    prev_txt = "\n".join(resume_prev) if resume_prev else "(Sin puntos previos aprobados)"

    answers_txt = "\n".join([f"- {k}: {v}" for k, v in answers.items() if v])
    return f"""{BASE_RULES}

Contexto aprobado hasta ahora:
{prev_txt}

Instrucción: redacta el punto "{point_name}" de la Memoria justificativa, en 1-3 párrafos, sin viñetas, con estilo administrativo, sin repetir lo ya aprobado. Evita citas legales innecesarias. Sé preciso.

Datos proporcionados para {point_name}:
{answers_txt}
"""
