"""Modelos de dados utilizados pela aplicação."""

from __future__ import annotations

from datetime import datetime

from . import db


class Certificate(db.Model):
    """Representa um certificado emitido pela instituição."""

    __tablename__ = "certificates"

    id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(255), nullable=False)
    cpf = db.Column(db.String(20), nullable=False)
    course_name = db.Column(db.String(255), nullable=False)
    workload_hours = db.Column(db.Integer, nullable=False)
    completion_date = db.Column(db.Date, nullable=False)
    issuer_name = db.Column(db.String(255))
    extra_info = db.Column(db.Text)
    validation_code = db.Column(db.String(20), unique=True, nullable=False, index=True)
    pdf_data = db.Column(db.LargeBinary, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:  # pragma: no cover - usado para debug
        return (
            f"<Certificate id={self.id!r} student_name={self.student_name!r} "
            f"course_name={self.course_name!r}>"
        )

    def as_dict(self) -> dict[str, str]:
        """Retorna os dados relevantes do certificado em formato de dicionário."""
        return {
            "student_name": self.student_name,
            "cpf": self.cpf,
            "course_name": self.course_name,
            "workload_hours": self.workload_hours,
            "completion_date": self.completion_date,
            "issuer_name": self.issuer_name,
            "extra_info": self.extra_info,
            "validation_code": self.validation_code,
            "created_at": self.created_at,
        }
