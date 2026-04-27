"""
Repository de Pedidos — acesso a dados das tabelas `pedidos` e `itens_pedido`.
"""

from app.repositories.db import conectar


def inserir_pedido(p: dict, itens: list[dict]) -> int | bool:
    """Insere pedido e seus itens em uma única transação. Retorna o ID ou False."""
    conn = conectar()
    try:
        cur = conn.execute(
            """INSERT INTO pedidos
               (cliente_nome, bairro, endereco, total_produtos, taxa_entrega, total_geral, metodo_pagamento, status)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                p.get("nome"),
                p.get("bairro"),
                p.get("endereco"),
                p.get("total_itens"),
                p.get("taxa"),
                p.get("total_geral"),
                p.get("metodo"),
                "Pendente",
            ),
        )
        pedido_id = cur.lastrowid

        conn.executemany(
            "INSERT INTO itens_pedido (pedido_id, produto_nome, quantidade, preco_unitario) VALUES (?, ?, ?, ?)",
            [
                (pedido_id, item.get("nome"), item.get("quantidade"), item.get("preco"))
                for item in itens
            ],
        )

        conn.commit()
        return pedido_id
    except Exception as e:
        conn.rollback()
        print(f"[PedidoRepository] Erro ao inserir pedido: {e}")
        return False
    finally:
        conn.close()


def buscar_pedidos(hora_inicio=None, dt_inicio=None, dt_fim=None) -> list[dict]:
    """Retorna pedidos com seus itens, com filtros opcionais."""
    conn = conectar()

    if dt_inicio and dt_fim:
        rows = conn.execute(
            "SELECT * FROM pedidos WHERE data_hora >= ? AND data_hora <= ? ORDER BY id DESC",
            (dt_inicio, dt_fim),
        ).fetchall()
    elif dt_inicio:
        rows = conn.execute(
            "SELECT * FROM pedidos WHERE data_hora >= ? ORDER BY id DESC", (dt_inicio,)
        ).fetchall()
    elif dt_fim:
        rows = conn.execute(
            "SELECT * FROM pedidos WHERE data_hora <= ? ORDER BY id DESC", (dt_fim,)
        ).fetchall()
    elif hora_inicio is not None:
        rows = conn.execute(
            "SELECT * FROM pedidos WHERE CAST(strftime('%H', data_hora) AS INTEGER) >= ? ORDER BY id DESC",
            (hora_inicio,),
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM pedidos ORDER BY id DESC").fetchall()

    pedidos = []
    for row in rows:
        p = dict(row)
        itens = conn.execute(
            "SELECT produto_nome, quantidade, preco_unitario FROM itens_pedido WHERE pedido_id = ?",
            (p["id"],),
        ).fetchall()
        p["itens"] = [dict(i) for i in itens]
        # Aliases para compatibilidade com templates legados
        p["data"] = p["data_hora"]
        p["total"] = p["total_geral"]
        p["metodo"] = p["metodo_pagamento"]
        pedidos.append(p)

    conn.close()
    return pedidos


def buscar_por_id_mp(id_mp: str) -> dict | None:
    conn = conectar()
    row = conn.execute(
        "SELECT id, status FROM pedidos WHERE id_pagamento_mp = ?", (str(id_mp),)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def buscar_itens(pedido_id: int) -> list[dict]:
    conn = conectar()
    rows = conn.execute(
        "SELECT * FROM itens_pedido WHERE pedido_id = ?", (pedido_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def atualizar_status(pedido_id: int, novo_status: str):
    conn = conectar()
    conn.execute("UPDATE pedidos SET status = ? WHERE id = ?", (novo_status, pedido_id))
    conn.commit()
    conn.close()


def vincular_id_mp(pedido_id: int, id_mp: str):
    conn = conectar()
    conn.execute(
        "UPDATE pedidos SET id_pagamento_mp = ? WHERE id = ?", (str(id_mp), pedido_id)
    )
    conn.commit()
    conn.close()


def deletar(pedido_id: int):
    conn = conectar()
    conn.execute("DELETE FROM pedidos WHERE id = ?", (pedido_id,))
    conn.commit()
    conn.close()
