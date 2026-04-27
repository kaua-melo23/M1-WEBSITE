from flask import Flask
from datetime import timedelta

from config.settings import Config
from app.repositories.db import init_db
from app.repositories.gpo_repository import init_gpo
from app.repositories.complemento_repository import init_complementos


def create_app(config_class=Config):
    """Application Factory — cria e configura a instância do Flask."""
    import os
    # Resolve os caminhos absolutos independente de onde o script é executado
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    template_dir = os.path.join(base_dir, "templates")
    static_dir = os.path.join(base_dir, "static")

    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
    app.config.from_object(config_class)

    # ── Configurações de sessão ───────────────────────────────────────
    app.config.update(
        SESSION_PERMANENT=True,
        PERMANENT_SESSION_LIFETIME=timedelta(hours=2),
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_REFRESH_EACH_REQUEST=True,
        SESSION_COOKIE_SECURE=False,
    )

    # ── Inicialização do banco de dados ──────────────────────────────
    init_db()
    init_gpo()
    init_complementos()

    # ── Registro dos Blueprints ──────────────────────────────────────
    from app.controllers.auth_controller import auth_bp
    from app.controllers.admin_controller import admin_bp
    from app.controllers.vendas_controller import vendas_bp
    from app.controllers.atendente_controller import atendente_bp
    from app.controllers.gpo_controller import gpo_bp
    from app.controllers.main_controller import main_bp
    from app.controllers.complemento_controller import complemento_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(vendas_bp)
    app.register_blueprint(atendente_bp)
    app.register_blueprint(gpo_bp)
    app.register_blueprint(complemento_bp)

    return app