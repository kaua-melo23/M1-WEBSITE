"""
Repository de Configurações, Categorias e Menu Admin.
"""

from app.repositories.db import conectar


# ── Configurações ─────────────────────────────────────────────────────

def buscar_configuracoes() -> dict:
    conn = conectar()
    rows = conn.execute("SELECT chave, valor FROM configuracoes").fetchall()
    conn.close()
    return {r["chave"]: r["valor"] for r in rows}


def salvar_configuracoes(dados: dict):
    conn = conectar()
    conn.executemany(
        "INSERT OR REPLACE INTO configuracoes (chave, valor) VALUES (?, ?)",
        list(dados.items()),
    )
    conn.commit()
    conn.close()


# ── Categorias do cliente ─────────────────────────────────────────────

def buscar_categorias(apenas_ativas: bool = False) -> list[dict]:
    conn = conectar()
    sql = "SELECT * FROM categorias_cliente"
    if apenas_ativas:
        sql += " WHERE ativo=1"
    sql += " ORDER BY ordem ASC"
    rows = conn.execute(sql).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def inserir_categoria(nome: str, emoji: str):
    conn = conectar()
    proxima = conn.execute("SELECT COALESCE(MAX(ordem),0)+1 FROM categorias_cliente").fetchone()[0]
    conn.execute(
        "INSERT INTO categorias_cliente (nome, emoji, ordem, ativo) VALUES (?, ?, ?, 1)",
        (nome, emoji, proxima),
    )
    conn.commit()
    conn.close()


def atualizar_categoria(cat_id: int, nome: str, emoji: str, ativo: int):
    conn = conectar()
    conn.execute(
        "UPDATE categorias_cliente SET nome=?, emoji=?, ativo=? WHERE id=?",
        (nome, emoji, ativo, cat_id),
    )
    conn.commit()
    conn.close()


def deletar_categoria(cat_id: int):
    conn = conectar()
    conn.execute("DELETE FROM categorias_cliente WHERE id=?", (cat_id,))
    conn.commit()
    conn.close()


def reordenar_categorias(ids_ordenados: list[int]):
    conn = conectar()
    conn.executemany(
        "UPDATE categorias_cliente SET ordem=? WHERE id=?",
        [(i, cat_id) for i, cat_id in enumerate(ids_ordenados)],
    )
    conn.commit()
    conn.close()


# ── Menu Admin ────────────────────────────────────────────────────────

def buscar_menu_admin(apenas_visiveis: bool = False) -> list[dict]:
    conn = conectar()
    sql = "SELECT * FROM menu_admin"
    if apenas_visiveis:
        sql += " WHERE visivel=1"
    sql += " ORDER BY ordem ASC"
    rows = conn.execute(sql).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def atualizar_item_menu(item_id: int, label: str, emoji: str, visivel: int):
    conn = conectar()
    conn.execute(
        "UPDATE menu_admin SET label=?, emoji=?, visivel=? WHERE id=?",
        (label, emoji, visivel, item_id),
    )
    conn.commit()
    conn.close()


def reordenar_menu_admin(ids_ordenados: list[int]):
    conn = conectar()
    conn.executemany(
        "UPDATE menu_admin SET ordem=? WHERE id=?",
        [(i, item_id) for i, item_id in enumerate(ids_ordenados)],
    )
    conn.commit()
    conn.close()


# ── Taxas de Entrega ──────────────────────────────────────────────────

def buscar_taxas() -> list[dict]:
    conn = conectar()
    rows = conn.execute("SELECT * FROM taxas_entrega ORDER BY bairro ASC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def salvar_taxa(bairro: str, valor: float):
    conn = conectar()
    conn.execute(
        "INSERT OR REPLACE INTO taxas_entrega (bairro, taxa) VALUES (?, ?)", (bairro, valor)
    )
    conn.commit()
    conn.close()


def deletar_taxa(taxa_id: int):
    conn = conectar()
    conn.execute("DELETE FROM taxas_entrega WHERE id = ?", (taxa_id,))
    conn.commit()
    conn.close()
