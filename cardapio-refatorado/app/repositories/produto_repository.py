"""
Repository de Produtos — acesso a dados da tabela `produtos`.

Nenhuma regra de negócio aqui: só SQL.
"""

from app.repositories.db import conectar


def buscar_todos() -> list[dict]:
    conn = conectar()
    rows = conn.execute("SELECT * FROM produtos ORDER BY id ASC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def buscar_visiveis() -> list[dict]:
    conn = conectar()
    rows = conn.execute(
        "SELECT * FROM produtos WHERE visivel = 1 ORDER BY id ASC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def buscar_por_id(produto_id: int) -> dict | None:
    conn = conectar()
    row = conn.execute("SELECT * FROM produtos WHERE id = ?", (produto_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def buscar_por_nome(nome: str) -> dict | None:
    conn = conectar()
    row = conn.execute("SELECT * FROM produtos WHERE nome = ?", (nome,)).fetchone()
    conn.close()
    return dict(row) if row else None


def inserir(nome: str, preco: float, categoria: str, imagem: str, ingredientes: str) -> int:
    conn = conectar()
    cur = conn.execute(
        "INSERT INTO produtos (nome, preco, categoria, imagem, ingredientes, visivel) VALUES (?, ?, ?, ?, ?, 1)",
        (nome, preco, categoria, imagem, ingredientes),
    )
    conn.commit()
    novo_id = cur.lastrowid
    conn.close()
    return novo_id


def atualizar(
    produto_id: int,
    nome: str,
    preco: float,
    categoria: str,
    imagem: str | None,
    ingredientes: str,
    visivel: int,
):
    conn = conectar()
    if imagem:
        conn.execute(
            "UPDATE produtos SET nome=?, preco=?, categoria=?, imagem=?, ingredientes=?, visivel=? WHERE id=?",
            (nome, preco, categoria, imagem, ingredientes, visivel, produto_id),
        )
    else:
        conn.execute(
            "UPDATE produtos SET nome=?, preco=?, categoria=?, ingredientes=?, visivel=? WHERE id=?",
            (nome, preco, categoria, ingredientes, visivel, produto_id),
        )
    conn.commit()
    conn.close()


def deletar(produto_id: int):
    conn = conectar()
    conn.execute("DELETE FROM produtos WHERE id = ?", (produto_id,))
    conn.commit()
    conn.close()
