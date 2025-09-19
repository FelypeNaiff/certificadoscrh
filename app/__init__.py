"""Aplicação principal de emissão e validação de certificados."""

from __future__ import annotations

import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Objeto de banco de dados compartilhado pelos módulos do aplicativo.
db = SQLAlchemy()


def create_app() -> Flask:
    """Cria e configura a aplicação Flask."""
    app = Flask(__name__, instance_relative_config=True)

    # Configurações básicas; podem ser sobrescritas por variáveis de ambiente.
    app.config.setdefault("SECRET_KEY", os.environ.get("SECRET_KEY", "dev"))

    default_db_path = os.path.join(app.instance_path, "certificates.sqlite")
    os.makedirs(app.instance_path, exist_ok=True)
    app.config.setdefault(
        "SQLALCHEMY_DATABASE_URI",
        os.environ.get("DATABASE_URL", f"sqlite:///{default_db_path}"),
    )
    app.config.setdefault("SQLALCHEMY_TRACK_MODIFICATIONS", False)

    app.config.setdefault("VALIDATION_URL", os.environ.get("VALIDATION_URL"))

    db.init_app(app)

    from . import models  # noqa: F401  # garante o registro dos modelos
    from . import routes

    app.register_blueprint(routes.bp)

    with app.app_context():
        db.create_all()

    return app


# Instância pronta para ser utilizada por servidores WSGI ou pelo comando ``flask run``.
app = create_app()
