"""
Utilitários de diagnóstico executados na inicialização do servidor.
"""

import os
from flask import current_app


def realizar_testes_iniciais():
    """Valida conexões e estrutura de diretórios na inicialização."""
    print("\n" + "=" * 50)
    print("🚀 DIAGNÓSTICO DE CONEXÃO E CREDENCIAIS")
    print("=" * 50)

    # Mercado Pago
    from app.services.pagamento_service import validar_conexao
    resultado = validar_conexao()
    icone = "✅" if resultado["ok"] else "❌"
    print(f"{icone} MERCADO PAGO: {resultado['msg']}")

    # Pastas necessárias
    pastas = [
        current_app.config.get("UPLOAD_FOLDER", "static/uploads"),
        os.path.dirname(current_app.config.get("DB_PATH", "database/lanchonete.db")),
    ]
    for pasta in pastas:
        if not os.path.exists(pasta):
            os.makedirs(pasta, exist_ok=True)
            print(f"📁 PASTA criada: {pasta}")

    print("=" * 50 + "\n")
