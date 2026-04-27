"""
Utilitários de upload de arquivos.
"""

import os
from flask import current_app
from werkzeug.utils import secure_filename


def extensao_permitida(filename: str) -> bool:
    allowed = current_app.config.get("ALLOWED_EXTENSIONS", {"png", "jpg", "jpeg", "gif", "webp"})
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed


def salvar_imagem(arquivo) -> str | None:
    """
    Salva o arquivo de imagem e retorna o nome do arquivo salvo,
    ou None se o arquivo for inválido.
    """
    if not arquivo or arquivo.filename == "":
        return None

    if not extensao_permitida(arquivo.filename):
        return None

    filename = secure_filename(arquivo.filename)
    upload_folder = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_folder, exist_ok=True)
    arquivo.save(os.path.join(upload_folder, filename))
    return filename
