"""
Service de Pagamento — integração com o Mercado Pago.

Isola totalmente a lógica de pagamento das rotas HTTP.
"""

from datetime import datetime, timedelta

import mercadopago
from flask import current_app


def _get_sdk() -> mercadopago.SDK:
    token = current_app.config["MP_ACCESS_TOKEN"]
    return mercadopago.SDK(token)


def gerar_pix(total: float, dados_pedido: dict) -> dict:
    """
    Cria um pagamento PIX com validade de 4 minutos.
    Armazena os dados do pedido no metadata para recuperação no webhook.
    """
    sdk = _get_sdk()
    expiracao = (datetime.now() + timedelta(minutes=4)).strftime("%Y-%m-%dT%H:%M:%S.000-03:00")

    payment_data = {
        "transaction_amount": total,
        "description": "Pagamento Lanchonete (Expira em 4min)",
        "payment_method_id": "pix",
        "date_of_expiration": expiracao,
        "payer": {
            "email": "cliente@email.com",
            "first_name": "Cliente",
            "identification": {"type": "CPF", "number": "12345678909"},
        },
        "metadata": {"dados_pedido": dados_pedido},
    }

    response = sdk.payment().create(payment_data)
    payment = response["response"]

    if "point_of_interaction" not in payment:
        return {"erro": "Erro ao gerar PIX", "detalhes": payment}

    return {
        "status": "pending",
        "id_mp": payment["id"],
        "pix_copia_cola": payment["point_of_interaction"]["transaction_data"]["qr_code"],
        "qr_code_img": payment["point_of_interaction"]["transaction_data"]["qr_code_base64"],
        "expires_at": expiracao,
    }


def consultar_pagamento(id_mp: str) -> dict | None:
    """Consulta o status de um pagamento no Mercado Pago."""
    sdk = _get_sdk()
    try:
        response = sdk.payment().get(id_mp)
        return response.get("response")
    except Exception as e:
        print(f"[PagamentoService] Erro ao consultar pagamento {id_mp}: {e}")
        return None


def validar_conexao() -> dict:
    """Testa a conexão e validade do token com o Mercado Pago."""
    sdk = _get_sdk()
    try:
        res = sdk.payment().search({"limit": 1})
        status_code = res.get("status")
        if status_code in [200, 201]:
            return {"ok": True, "msg": f"Conexão e Token OK (Status {status_code})"}
        elif status_code == 401:
            return {"ok": False, "msg": "Token INVÁLIDO (Erro 401 - Unauthorized)"}
        return {"ok": False, "msg": f"Resposta inesperada (Status {status_code})"}
    except Exception as e:
        return {"ok": False, "msg": f"Falha técnica na conexão: {e}"}
