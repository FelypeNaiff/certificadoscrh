"""Utilitários para geração do certificado em PDF."""

from __future__ import annotations

from datetime import date
from typing import Optional

from fpdf import FPDF

MONTH_NAMES_PT = [
    "janeiro",
    "fevereiro",
    "março",
    "abril",
    "maio",
    "junho",
    "julho",
    "agosto",
    "setembro",
    "outubro",
    "novembro",
    "dezembro",
]


def format_date_pt_br(value: date) -> str:
    """Formata uma data no padrão textual brasileiro."""
    return f"{value.day} de {MONTH_NAMES_PT[value.month - 1]} de {value.year}"


def build_certificate_pdf(
    *,
    student_name: str,
    cpf: str,
    course_name: str,
    workload_hours: int,
    completion_date: date,
    validation_code: str,
    validation_url: str,
    issuer_name: Optional[str] = None,
    extra_info: Optional[str] = None,
) -> bytes:
    """Gera um certificado em PDF a partir dos dados informados."""

    pdf = FPDF(orientation="L", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=False)
    pdf.add_page()

    pdf.set_fill_color(248, 249, 250)
    pdf.rect(10, 10, 277, 190, style="F")

    pdf.set_font("Helvetica", "B", 36)
    pdf.set_text_color(33, 37, 41)
    pdf.cell(0, 30, "Certificado de Conclusão", border=0, ln=1, align="C")

    pdf.ln(10)
    pdf.set_font("Helvetica", size=18)
    body_text = (
        f"Certificamos que {student_name} (CPF: {cpf}) concluiu o curso "
        f"\"{course_name}\" com carga horária total de {workload_hours} horas, "
        f"finalizado em {format_date_pt_br(completion_date)}."
    )
    pdf.multi_cell(0, 10, body_text, align="C")

    if extra_info:
        pdf.ln(4)
        pdf.set_font("Helvetica", size=14)
        pdf.multi_cell(0, 8, extra_info, align="C")

    pdf.ln(20)
    pdf.set_font("Helvetica", "", 16)
    if issuer_name:
        pdf.cell(0, 10, issuer_name, ln=1, align="C")
        pdf.cell(0, 6, "Responsável pela emissão", ln=1, align="C")
    else:
        pdf.cell(0, 10, "Instituição de Ensino", ln=1, align="C")

    pdf.ln(15)
    pdf.set_font("Helvetica", size=12)
    pdf.set_text_color(73, 80, 87)
    pdf.cell(0, 8, f"Código de validação: {validation_code}", ln=1, align="C")
    pdf.multi_cell(0, 8, f"Valide este certificado em {validation_url}", align="C")

    # ``output`` com ``dest='S'`` retorna uma ``str`` codificada em Latin-1.
    return pdf.output(dest="S").encode("latin-1")
