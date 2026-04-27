"""
Ponto de entrada da aplicação.

Para desenvolvimento: python run.py
Para produção: gunicorn "run:create_app()"
"""

from app import create_app
from config.settings import Config

app = create_app(Config)

if __name__ == "__main__":
    with app.app_context():
        from app.utils.diagnostico import realizar_testes_iniciais
        realizar_testes_iniciais()

    app.run(
        debug=Config.DEBUG,
        host=Config.HOST,
        port=Config.PORT,
    )
