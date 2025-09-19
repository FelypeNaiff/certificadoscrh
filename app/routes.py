"""Rotas da aplicação de emissão e validação de certificados."""

from __future__ import annotations

import io
import secrets
import string
from datetime import datetime
from typing import Any, Dict, Optional

from flask import (
    Blueprint,
    Response,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    send_file,
    url_for,
)
from werkzeug.utils import secure_filename

from . import db
from .models import Certificate
from .pdf import build_certificate_pdf

bp = Blueprint("main", __name__)

CODE_ALPHABET = string.ascii_uppercase + string.digits


def generate_validation_code(length: int = 10) -> str:
    """Gera um código único de validação."""
    while True:
        code = "".join(secrets.choice(CODE_ALPHABET) for _ in range(length))
        if not Certificate.query.filter_by(validation_code=code).first():
            return code


def build_validation_link(validation_code: str) -> str:
    """Retorna o link completo para validação de um certificado."""
    base_url = current_app.config.get("VALIDATION_URL")
    if base_url:
        base_url = base_url.rstrip("/")
    else:
        base_url = url_for("main.validate_certificate", _external=True).rstrip("/")
    return f"{base_url}?code={validation_code}"


def parse_completion_date(value: str) -> Optional[datetime.date]:
    """Converte uma string de data (YYYY-MM-DD) em um objeto date."""
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


@bp.route("/", methods=["GET", "POST"])
def validate_certificate() -> str:
    """Página pública para validação de certificados."""
    certificate: Optional[Certificate] = None
    error: Optional[str] = None

    code_input = ""
    triggered_lookup = False
    if request.method == "POST":
        code_input = request.form.get("validation_code", "")
        triggered_lookup = True
    else:
        code_input = request.args.get("code", "")
        triggered_lookup = bool(code_input)

    code = code_input.strip().upper()

    if triggered_lookup:
        if not code:
            error = "Informe o código de validação."
        else:
            certificate = Certificate.query.filter_by(validation_code=code).first()
            if certificate is None:
                error = "Certificado não encontrado ou inválido."

    return render_template(
        "validate.html",
        certificate=certificate,
        code=code_input.strip(),
        error=error,
    )


@bp.route("/admin", methods=["GET", "POST"])
def admin_issue_certificate() -> str:
    """Formulário administrativo para emissão de certificados."""
    form_data: Dict[str, Any] = dict(request.form) if request.method == "POST" else {}
    if request.method == "POST":
        student_name = request.form.get("student_name", "").strip()
        cpf = request.form.get("cpf", "").strip()
        course_name = request.form.get("course_name", "").strip()
        workload_hours_raw = request.form.get("workload_hours", "").strip()
        completion_date_raw = request.form.get("completion_date", "").strip()
        issuer_name = request.form.get("issuer_name", "").strip() or None
        extra_info = request.form.get("extra_info", "").strip() or None

        errors = []
        if not student_name:
            errors.append("Informe o nome completo do aluno.")
        if not cpf:
            errors.append("Informe o CPF do aluno.")
        if not course_name:
            errors.append("Informe o nome do curso.")

        workload_hours: Optional[int] = None
        try:
            workload_hours = int(workload_hours_raw)
        except ValueError:
            errors.append("Informe a carga horária em horas (valor numérico).")
        else:
            if workload_hours <= 0:
                errors.append("A carga horária deve ser maior que zero.")
                workload_hours = None

        completion_date = parse_completion_date(completion_date_raw)
        if completion_date is None:
            errors.append("Informe uma data de conclusão válida.")

        if errors:
            for message in errors:
                flash(message, "error")
            return render_template("admin_form.html", form_data=form_data)

        assert workload_hours is not None  # for type checkers

        validation_code = generate_validation_code()
        validation_link = build_validation_link(validation_code)

        pdf_data = build_certificate_pdf(
            student_name=student_name,
            cpf=cpf,
            course_name=course_name,
            workload_hours=workload_hours,
            completion_date=completion_date,
            issuer_name=issuer_name,
            extra_info=extra_info,
            validation_code=validation_code,
            validation_url=validation_link,
        )

        certificate = Certificate(
            student_name=student_name,
            cpf=cpf,
            course_name=course_name,
            workload_hours=workload_hours,
            completion_date=completion_date,
            issuer_name=issuer_name,
            extra_info=extra_info,
            validation_code=validation_code,
            pdf_data=pdf_data,
        )
        db.session.add(certificate)
        db.session.commit()

        flash("Certificado emitido com sucesso!", "success")
        return redirect(
            url_for("main.admin_certificate_detail", certificate_id=certificate.id)
        )

    return render_template("admin_form.html", form_data=form_data)


@bp.route("/admin/certificates")
def admin_list_certificates() -> str:
    """Lista todos os certificados emitidos."""
    certificates = Certificate.query.order_by(Certificate.created_at.desc()).all()
    return render_template("admin_list.html", certificates=certificates)


@bp.route("/admin/certificates/<int:certificate_id>")
def admin_certificate_detail(certificate_id: int) -> str:
    """Mostra os detalhes de um certificado específico."""
    certificate = Certificate.query.get_or_404(certificate_id)
    validation_link = build_validation_link(certificate.validation_code)
    return render_template(
        "admin_detail.html",
        certificate=certificate,
        validation_link=validation_link,
    )


@bp.route("/certificates/<string:code>/download")
def download_certificate(code: str) -> Response:
    """Disponibiliza o certificado em PDF para download."""
    certificate = Certificate.query.filter_by(validation_code=code.upper()).first_or_404()

    filename = secure_filename(f"certificado-{certificate.student_name}.pdf") or (
        f"certificado-{certificate.validation_code}.pdf"
    )

    return send_file(
        io.BytesIO(certificate.pdf_data),
        mimetype="application/pdf",
        as_attachment=True,
        download_name=filename,
    )
