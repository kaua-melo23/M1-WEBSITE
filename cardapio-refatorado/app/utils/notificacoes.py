"""
Utilitários de notificação (WhatsApp, e-mail, etc.).

Atualmente simulado via print — substitua pelo SDK real quando necessário.
"""

from app.repositories import pedido_repository as repo


def enviar_pedido_whatsapp(pedido_id: int):
    """
    Gera e imprime o resumo do pedido no formato WhatsApp.
    Para integração real, substitua o `print` pela chamada à API de mensagens.
    """
    try:
        conn_rows = repo.buscar_itens(pedido_id)

        from app.repositories.db import conectar
        conn = conectar()
        pedido = conn.execute("SELECT * FROM pedidos WHERE id = ?", (pedido_id,)).fetchone()
        conn.close()

        if not pedido:
            return

        resumo_itens = "\n".join(
            [f"- {i['quantidade']}x {i['produto_nome']}" for i in conn_rows]
        )
        mensagem = (
            f"🔔 *NOVO PEDIDO #{pedido_id}*\n\n"
            f"👤 *Cliente:* {pedido['cliente_nome']}\n"
            f"📍 *Endereço:* {pedido['endereco']}\n"
            f"💳 *Método:* {pedido['metodo_pagamento']}\n"
            f"--------------------------\n"
            f"🛒 *Itens:*\n{resumo_itens}\n"
            f"--------------------------\n"
            f"💰 *Total:* R$ {pedido['total_geral']:.2f}\n"
            f"🆔 *Cód. Pedido:* #{pedido_id}"
        )
        print("\n=== DISPARO WHATSAPP ===\n", mensagem)
    except Exception as e:
        print(f"[Notificacoes] Erro ao enviar WhatsApp: {e}")
