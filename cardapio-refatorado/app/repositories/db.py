"""
Camada de infraestrutura — conexão e inicialização do banco de dados.

Responsabilidade única: abrir/fechar conexões e criar o schema.
Regras de negócio ficam nos Services; consultas ficam nos Repositories.
"""

import sqlite3
import json
import os
from flask import current_app


def get_db_path() -> str:
    """Retorna o caminho do banco. Usa o app context quando disponível."""
    try:
        return current_app.config["DB_PATH"]
    except RuntimeError:
        # Fora do contexto Flask (ex.: scripts de migração)
        base = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        return os.path.join(base, "database", "lanchonete.db")


def conectar() -> sqlite3.Connection:
    """Abre e retorna uma conexão com o banco de dados."""
    db_path = get_db_path()
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


# ── Schema ────────────────────────────────────────────────────────────

_DDL_TABELAS = """
CREATE TABLE IF NOT EXISTS produtos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    preco REAL NOT NULL,
    categoria TEXT,
    imagem TEXT,
    ingredientes TEXT,
    visivel INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS taxas_entrega (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bairro TEXT UNIQUE NOT NULL,
    taxa REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS pedidos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    cliente_nome TEXT,
    bairro TEXT,
    endereco TEXT,
    total_produtos REAL,
    taxa_entrega REAL,
    total_geral REAL,
    metodo_pagamento TEXT,
    status TEXT DEFAULT 'Pendente',
    id_pagamento_mp TEXT
);

CREATE TABLE IF NOT EXISTS itens_pedido (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pedido_id INTEGER,
    produto_nome TEXT,
    quantidade INTEGER,
    preco_unitario REAL,
    FOREIGN KEY (pedido_id) REFERENCES pedidos (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS insumos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    unidade_base TEXT NOT NULL,
    estoque_minimo REAL DEFAULT 0,
    tipo TEXT DEFAULT 'bruto',
    validade_padrao DATE
);

CREATE TABLE IF NOT EXISTS lotes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    insumo_id INTEGER,
    quantidade_inicial REAL,
    quantidade_atual REAL,
    validade DATE,
    custo_lote REAL,
    data_entrada DATE,
    FOREIGN KEY (insumo_id) REFERENCES insumos (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS receitas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    insumo_fabricado_id INTEGER NOT NULL,
    insumo_bruto_id INTEGER NOT NULL,
    quantidade REAL NOT NULL,
    FOREIGN KEY (insumo_fabricado_id) REFERENCES insumos (id) ON DELETE CASCADE,
    FOREIGN KEY (insumo_bruto_id) REFERENCES insumos (id)
);

CREATE TABLE IF NOT EXISTS produto_insumo (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    produto_id INTEGER NOT NULL,
    insumo_id INTEGER NOT NULL,
    quantidade REAL NOT NULL DEFAULT 1,
    FOREIGN KEY (produto_id) REFERENCES produtos (id) ON DELETE CASCADE,
    FOREIGN KEY (insumo_id) REFERENCES insumos (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS configuracoes (
    chave TEXT PRIMARY KEY,
    valor TEXT
);

CREATE TABLE IF NOT EXISTS categorias_cliente (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    emoji TEXT DEFAULT '🍽️',
    ordem INTEGER DEFAULT 0,
    ativo INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS menu_admin (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    label TEXT NOT NULL,
    url TEXT NOT NULL,
    emoji TEXT DEFAULT '📄',
    ordem INTEGER DEFAULT 0,
    visivel INTEGER DEFAULT 1
);
"""

_CONFIGS_PADRAO = [
    ("nome_lanchonete", "Lanchonete Express"),
    ("slogan", "O melhor sabor da região"),
    ("cor_primaria", "#dc2626"),
    ("cor_texto_header", "#ffffff"),
    ("logo_url", ""),
    ("hora_abertura", "18:00"),
    ("hora_fechamento", "23:00"),
]

_CATEGORIAS_PADRAO = [
    ("Lanches", "🍔", 0),
    ("Bebidas", "🥤", 1),
    ("Porções", "🍟", 2),
    ("Sobremesas", "🍨", 3),
]

_MENU_ADMIN_PADRAO = [
    ("Dashboard", "/admin", "📊", 0),
    ("Relatórios", "/admin/relatorios", "📈", 1),
    ("Estoque", "/admin/estoque", "📦", 2),
    ("Produtos", "/admin/produtos", "🍔", 3),
    ("Complementos", "/admin/complementos", "🍓", 4),
    ("Pedidos", "/admin/pedidos", "🛵", 5),
    ("Taxas", "/admin/taxas", "📍", 6),
    ("Aparência", "/admin/aparencia", "🎨", 7),
    ("Navegação", "/admin/navegacao", "🗂️", 8),
    ("GPO", "/admin/gpo", "👥", 9),
]

_MIGRACOES = [
    ("ALTER TABLE produtos ADD COLUMN ingredientes TEXT", None),
    ("ALTER TABLE produtos ADD COLUMN visivel INTEGER DEFAULT 1",
     "UPDATE produtos SET visivel = 1 WHERE visivel IS NULL"),
    ("ALTER TABLE insumos ADD COLUMN tipo TEXT DEFAULT 'bruto'",
     "UPDATE insumos SET tipo = 'bruto' WHERE tipo IS NULL"),
    ("ALTER TABLE insumos ADD COLUMN validade_padrao DATE", None),
]


def init_db():
    """Cria tabelas, insere valores padrão e executa migrações."""
    conn = conectar()
    cur = conn.cursor()

    # Cria tabelas
    cur.executescript(_DDL_TABELAS)

    # Valores padrão de configurações
    for chave, valor in _CONFIGS_PADRAO:
        cur.execute(
            "INSERT OR IGNORE INTO configuracoes (chave, valor) VALUES (?, ?)",
            (chave, valor),
        )

    # Categorias padrão
    cur.execute("SELECT COUNT(*) FROM categorias_cliente")
    if cur.fetchone()[0] == 0:
        cur.executemany(
            "INSERT INTO categorias_cliente (nome, emoji, ordem, ativo) VALUES (?, ?, ?, 1)",
            _CATEGORIAS_PADRAO,
        )

    # Menu admin padrão
    cur.execute("SELECT COUNT(*) FROM menu_admin")
    if cur.fetchone()[0] == 0:
        cur.executemany(
            "INSERT INTO menu_admin (label, url, emoji, ordem, visivel) VALUES (?, ?, ?, ?, 1)",
            _MENU_ADMIN_PADRAO,
        )

    conn.commit()

    # Migrações incrementais
    for sql, followup in _MIGRACOES:
        try:
            cur.execute(sql)
            if followup:
                cur.execute(followup)
            conn.commit()
        except Exception:
            pass  # Coluna já existe

    # Garante que o item GPO existe no menu
    cur.execute("SELECT COUNT(*) FROM menu_admin WHERE url = '/admin/gpo'")
    if cur.fetchone()[0] == 0:
        cur.execute("SELECT COALESCE(MAX(ordem), 0) + 1 FROM menu_admin")
        proxima_ordem = cur.fetchone()[0]
        cur.execute(
            "INSERT INTO menu_admin (label, url, emoji, ordem, visivel) VALUES (?, ?, ?, ?, 1)",
            ("GPO", "/admin/gpo", "👥", proxima_ordem),
        )
        conn.commit()

    # Garante que o item Complementos existe no menu
    cur.execute("SELECT COUNT(*) FROM menu_admin WHERE url = '/admin/complementos'")
    if cur.fetchone()[0] == 0:
        cur.execute("SELECT COALESCE(MAX(ordem), 0) + 1 FROM menu_admin")
        proxima_ordem = cur.fetchone()[0]
        cur.execute(
            "INSERT INTO menu_admin (label, url, emoji, ordem, visivel) VALUES (?, ?, ?, ?, 1)",
            ("Complementos", "/admin/complementos", "🍓", proxima_ordem),
        )
        conn.commit()

    conn.close()
