import os
import streamlit as st
from typing import Dict
from exporter import export_basic, export_with_template
from prompts import CHECKLISTS, build_prompt

def generate_text_with_openai(prompt: str) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return (
            "Borrador (modo local sin API):\n"
            + prompt.split("Datos proporcionados para",1)[-1].strip()[:800]
            + "\n[Este es un texto de ejemplo; configure OPENAI_API_KEY para redacción real]"
        )
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role":"system","content":"Eres un técnico de Contratación Pública. Redactas en español, estilo administrativo, claro y preciso."},
                {"role":"user","content": prompt}
            ],
            temperature=0.2,
        )
        content = resp.choices[0].message.content
        return content.strip()
    except Exception as e:
        return f"Error al llamar a OpenAI: {e}"

POINTS = ["OBJETO","NECESIDAD","INSUFICIENCIA_MEDIOS"]

st.set_page_config(page_title="Memoria LCSP por pasos", layout="wide")
st.title("Memoria justificativa LCSP — Asistente por pasos")

if "answers" not in st.session_state:
    st.session_state.answers = {p:{} for p in POINTS}
if "drafts" not in st.session_state:
    st.session_state.drafts = {p:"" for p in POINTS}
if "approved" not in st.session_state:
    st.session_state.approved = {p:"" for p in POINTS}
if "current_idx" not in st.session_state:
    st.session_state.current_idx = 0

with st.sidebar:
    st.header("Puntos")
    for i, p in enumerate(POINTS):
        label = f"{i+1}. {p}"
        if st.session_state.approved[p]:
            label += " ✅"
        if st.button(label, key=f"nav_{p}"):
            st.session_state.current_idx = i

    st.markdown("---")
    st.subheader("Exportar")
    export_mode = st.radio("Modo", ["Plantilla DOCX", "Documento básico"], horizontal=True)
    template_file = None
    if export_mode == "Plantilla DOCX":
        template_file = st.file_uploader("Plantilla con placeholders {{OBJETO}}, {{NECESIDAD}}, etc.", type=["docx"])
    if st.button("Descargar DOCX"):
        data: Dict[str,str] = {k: v for k, v in st.session_state.approved.items() if v}
        if not data:
            st.warning("No hay puntos aprobados todavía.")
        else:
            out_name = "Memoria_borrador.docx"
            if export_mode == "Plantilla DOCX" and template_file is not None:
                import tempfile
                with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
                    tmp.write(template_file.read())
                    tmp_path = tmp.name
                export_with_template(tmp_path, data, out_name)
            else:
                export_basic(data, out_name)
            with open(out_name, "rb") as f:
                st.download_button("Descargar archivo", f, file_name=out_name, mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

p = POINTS[st.session_state.current_idx]
st.subheader(f"Punto {st.session_state.current_idx+1}: {p}")

answers = st.session_state.answers[p]
from prompts import CHECKLISTS
for q in CHECKLISTS.get(p, []):
    answers[q] = st.text_input(q, value=answers.get(q,""))

col1, col2, col3 = st.columns([1,1,1])
with col1:
    if st.button("Generar borrador"):
        prompt = build_prompt(p, answers, st.session_state.approved)
        st.session_state.drafts[p] = generate_text_with_openai(prompt)
with col2:
    if st.button("Aprobar punto"):
        draft = st.session_state.drafts[p].strip()
        if not draft:
            st.warning("Primero genera el borrador.")
        else:
            st.session_state.approved[p] = draft
            if st.session_state.current_idx < len(POINTS)-1:
                st.session_state.current_idx += 1
with col3:
    if st.button("Limpiar borrador"):
        st.session_state.drafts[p] = ""

st.markdown("### Borrador")
st.write(st.session_state.drafts[p] or "_Aún no hay borrador. Completa datos y pulsa **Generar borrador**._")

st.markdown("### Punto aprobado")
st.write(st.session_state.approved[p] or "_Aún no aprobado._")
