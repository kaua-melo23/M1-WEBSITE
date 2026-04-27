"""
Repository de Estoque — acesso a dados de insumos, lotes, receitas e vínculos produto→insumo.
"""

from app.repositories.db import conectar


# ── Insumos ───────────────────────────────────────────────────────────

def buscar_insumos(tipo: str | None = None) -> list[dict]:
    conn = conectar()
    sql = """
        SELECT i.*,
               COALESCE(SUM(CASE WHEN l.validade >= date('now') THEN l.quantidade_atual ELSE 0 END), 0) AS total_estoque,
               MIN(CASE WHEN l.validade >= date('now') AND l.quantidade_atual > 0 THEN l.validade END) AS proxima_validade
        FROM insumos i
        LEFT JOIN lotes l ON i.id = l.insumo_id
    """
    if tipo:
        rows = conn.execute(sql + " WHERE i.tipo = ? GROUP BY i.id ORDER BY i.nome", (tipo,)).fetchall()
    else:
        rows = conn.execute(sql + " GROUP BY i.id ORDER BY i.nome").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def inserir_insumo(nome: str, unidade_base: str, estoque_minimo: float, tipo: str, validade_padrao) -> int:
    conn = conectar()
    cur = conn.execute(
        "INSERT INTO insumos (nome, unidade_base, estoque_minimo, tipo, validade_padrao) VALUES (?, ?, ?, ?, ?)",
        (nome, unidade_base, estoque_minimo, tipo, validade_padrao),
    )
    conn.commit()
    novo_id = cur.lastrowid
    conn.close()
    return novo_id


def atualizar_insumo(insumo_id: int, nome: str, unidade_base: str, estoque_minimo: float, validade_padrao):
    conn = conectar()
    conn.execute(
        "UPDATE insumos SET nome=?, unidade_base=?, estoque_minimo=?, validade_padrao=? WHERE id=?",
        (nome, unidade_base, estoque_minimo, validade_padrao, insumo_id),
    )
    conn.commit()
    conn.close()


def deletar_insumo(insumo_id: int):
    conn = conectar()
    conn.execute("DELETE FROM insumos WHERE id=?", (insumo_id,))
    conn.commit()
    conn.close()


def buscar_insumo_por_nome(nome: str) -> dict | None:
    conn = conectar()
    row = conn.execute("SELECT id FROM insumos WHERE nome = ?", (nome,)).fetchone()
    conn.close()
    return dict(row) if row else None


# ── Lotes ─────────────────────────────────────────────────────────────

def buscar_lotes(insumo_id: int) -> list[dict]:
    conn = conectar()
    rows = conn.execute(
        """SELECT *,
               CASE WHEN validade < date('now') THEN 1 ELSE 0 END AS vencido,
               CASE WHEN validade <= date('now', '+7 days') AND validade >= date('now') THEN 1 ELSE 0 END AS vence_em_breve
           FROM lotes WHERE insumo_id = ? ORDER BY validade ASC""",
        (insumo_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def buscar_lotes_ativos(insumo_id: int) -> list[dict]:
    """Lotes válidos com estoque, ordenados por PVPS (primeiro que vence primeiro sai)."""
    conn = conectar()
    rows = conn.execute(
        """SELECT id, quantidade_atual, validade FROM lotes
           WHERE insumo_id = ? AND quantidade_atual > 0 AND validade >= date('now')
           ORDER BY validade ASC""",
        (insumo_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def estoque_disponivel(insumo_id: int) -> float:
    conn = conectar()
    row = conn.execute(
        "SELECT COALESCE(SUM(quantidade_atual), 0) AS total FROM lotes WHERE insumo_id = ? AND validade >= date('now')",
        (insumo_id,),
    ).fetchone()
    conn.close()
    return row["total"] if row else 0.0


def inserir_lote(insumo_id: int, quantidade: float, validade: str, custo: float = 0.0):
    conn = conectar()
    conn.execute(
        "INSERT INTO lotes (insumo_id, quantidade_inicial, quantidade_atual, validade, custo_lote, data_entrada) VALUES (?, ?, ?, ?, ?, date('now'))",
        (insumo_id, quantidade, quantidade, validade, custo),
    )
    conn.commit()
    conn.close()


def descontar_lote(lote_id: int, quantidade: float):
    conn = conectar()
    conn.execute(
        "UPDATE lotes SET quantidade_atual = quantidade_atual - ? WHERE id=?",
        (quantidade, lote_id),
    )
    conn.commit()
    conn.close()


# ── Receitas ──────────────────────────────────────────────────────────

def buscar_receita(insumo_fabricado_id: int) -> list[dict]:
    conn = conectar()
    rows = conn.execute(
        """SELECT r.*, i.nome AS nome_bruto, i.unidade_base
           FROM receitas r
           JOIN insumos i ON r.insumo_bruto_id = i.id
           WHERE r.insumo_fabricado_id = ?""",
        (insumo_fabricado_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def salvar_receita(insumo_fabricado_id: int, ingredientes: list[dict]):
    conn = conectar()
    conn.execute("DELETE FROM receitas WHERE insumo_fabricado_id=?", (insumo_fabricado_id,))
    conn.executemany(
        "INSERT INTO receitas (insumo_fabricado_id, insumo_bruto_id, quantidade) VALUES (?, ?, ?)",
        [(insumo_fabricado_id, i["insumo_bruto_id"], i["quantidade"]) for i in ingredientes],
    )
    conn.commit()
    conn.close()


def buscar_ingredientes_receita(insumo_fabricado_id: int, quantidade_produzida: float) -> list[dict]:
    conn = conectar()
    rows = conn.execute(
        """SELECT r.insumo_bruto_id, r.quantidade * ? AS qtd_necessaria, i.nome
           FROM receitas r
           JOIN insumos i ON r.insumo_bruto_id = i.id
           WHERE r.insumo_fabricado_id = ?""",
        (quantidade_produzida, insumo_fabricado_id),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ── Vínculos Produto → Insumo ─────────────────────────────────────────

def buscar_vinculos_produto(produto_id: int) -> list[dict]:
    conn = conectar()
    rows = conn.execute(
        """SELECT pi.*, i.nome AS nome_insumo, i.unidade_base, i.tipo
           FROM produto_insumo pi
           JOIN insumos i ON pi.insumo_id = i.id
           WHERE pi.produto_id = ?""",
        (produto_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def buscar_vinculos_por_produto_id(produto_id: int, quantidade_vendida: float) -> list[dict]:
    conn = conectar()
    rows = conn.execute(
        "SELECT pi.insumo_id, pi.quantidade * ? AS qtd_descontar FROM produto_insumo pi WHERE pi.produto_id = ?",
        (quantidade_vendida, produto_id),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def salvar_vinculos_produto(produto_id: int, insumos: list[dict]):
    conn = conectar()
    conn.execute("DELETE FROM produto_insumo WHERE produto_id=?", (produto_id,))
    conn.executemany(
        "INSERT INTO produto_insumo (produto_id, insumo_id, quantidade) VALUES (?, ?, ?)",
        [(produto_id, i["insumo_id"], i["quantidade"]) for i in insumos],
    )
    conn.commit()
    conn.close()


# ── Alertas ───────────────────────────────────────────────────────────

def buscar_alertas_estoque() -> list[dict]:
    conn = conectar()
    rows = conn.execute(
        """SELECT i.nome, i.unidade_base, i.tipo, i.estoque_minimo,
                  COALESCE(SUM(CASE WHEN l.validade >= date('now') THEN l.quantidade_atual ELSE 0 END), 0) AS total_estoque
           FROM insumos i
           LEFT JOIN lotes l ON i.id = l.insumo_id
           GROUP BY i.id
           HAVING total_estoque <= i.estoque_minimo AND i.estoque_minimo > 0
           ORDER BY (total_estoque / NULLIF(i.estoque_minimo, 0)) ASC"""
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
