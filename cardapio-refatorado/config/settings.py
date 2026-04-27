import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


class Config:
    # ── Flask ──────────────────────────────────────────────────────
    SECRET_KEY = os.getenv("SECRET_KEY", "chave-super-secreta-2026")
    DEBUG = os.getenv("FLASK_DEBUG", "false").lower() == "true"

    # ── Mercado Pago ───────────────────────────────────────────────
    MP_ACCESS_TOKEN = os.getenv("MP_ACCESS_TOKEN", "")

    # ── Banco de Dados ─────────────────────────────────────────────
    DB_PATH = os.path.join(BASE_DIR, "database", "lanchonete.db")

    # ── Upload de Arquivos ─────────────────────────────────────────
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp", "avif"}

    # ── Admin padrão (variáveis de ambiente) ───────────────────────
    ADMIN_USER = os.getenv("ADMIN_USER", "admin")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "1234")

    # ── Servidor ───────────────────────────────────────────────────
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 80))
