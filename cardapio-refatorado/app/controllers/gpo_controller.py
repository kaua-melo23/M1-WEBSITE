"""
Controller de GPO (Gestão de Pessoas e Organização).
"""

from flask import Blueprint, render_template, request, jsonify, redirect

from app.middleware.auth import admin_required
from app.repositories import gpo_repository
from app.repositories.gpo_repository import PERMISSOES_SISTEMA, ROLES_SISTEMA

gpo_bp = Blueprint("gpo_bp", __name__)


@gpo_bp.route("/admin/gpo")
@admin_required
def gpo_index():
    return render_template("admin/gpo.html")


# ── Usuários ──────────────────────────────────────────────────────────

@gpo_bp.route("/api/gpo/usuarios", methods=["GET"])
@admin_required
def api_listar_usuarios():
    return jsonify(gpo_repository.buscar_usuarios())


@gpo_bp.route("/api/gpo/usuarios", methods=["POST"])
@admin_required
def api_criar_usuario():
    d = request.get_json()
    if not d.get("username") or not d.get("senha") or not d.get("nome"):
        return jsonify({"ok": False, "erro": "Campos obrigatórios: username, senha, nome"}), 400
    result = gpo_repository.inserir_usuario(
        d["username"], d["senha"], d["nome"],
        d.get("role", "atendente"),
        d.get("grupo_id") or None,
    )
    return jsonify(result)


@gpo_bp.route("/api/gpo/usuarios/<int:uid>", methods=["PUT"])
@admin_required
def api_atualizar_usuario(uid):
    d = request.get_json()
    gpo_repository.atualizar_usuario(
        uid, d.get("nome", ""), d.get("role", "atendente"),
        d.get("grupo_id") or None, d.get("ativo", 1),
        d.get("senha") or None,
    )
    return jsonify({"ok": True})


@gpo_bp.route("/api/gpo/usuarios/<int:uid>", methods=["DELETE"])
@admin_required
def api_deletar_usuario(uid):
    gpo_repository.deletar_usuario(uid)
    return jsonify({"ok": True})


# ── Grupos ────────────────────────────────────────────────────────────

@gpo_bp.route("/api/gpo/grupos", methods=["GET"])
@admin_required
def api_listar_grupos():
    grupos = gpo_repository.buscar_grupos()
    for g in grupos:
        pols = gpo_repository.buscar_politicas_do_grupo(g["id"])
        g["politicas_ids"] = [p["id"] for p in pols]
        g["politicas_nomes"] = [p["nome"] for p in pols]
    return jsonify(grupos)


@gpo_bp.route("/api/gpo/grupos", methods=["POST"])
@admin_required
def api_criar_grupo():
    d = request.get_json()
    if not d.get("nome"):
        return jsonify({"ok": False, "erro": "Nome obrigatório"}), 400
    return jsonify(gpo_repository.inserir_grupo(d["nome"], d.get("descricao", "")))


@gpo_bp.route("/api/gpo/grupos/<int:gid>", methods=["PUT"])
@admin_required
def api_atualizar_grupo(gid):
    d = request.get_json()
    gpo_repository.atualizar_grupo(gid, d.get("nome", ""), d.get("descricao", ""))
    if "politicas_ids" in d:
        gpo_repository.sincronizar_politicas_grupo(gid, d["politicas_ids"])
    return jsonify({"ok": True})


@gpo_bp.route("/api/gpo/grupos/<int:gid>", methods=["DELETE"])
@admin_required
def api_deletar_grupo(gid):
    gpo_repository.deletar_grupo(gid)
    return jsonify({"ok": True})


# ── Políticas ─────────────────────────────────────────────────────────

@gpo_bp.route("/api/gpo/politicas", methods=["GET"])
@admin_required
def api_listar_politicas():
    return jsonify(gpo_repository.buscar_politicas())


@gpo_bp.route("/api/gpo/politicas", methods=["POST"])
@admin_required
def api_criar_politica():
    d = request.get_json()
    if not d.get("nome"):
        return jsonify({"ok": False, "erro": "Nome obrigatório"}), 400
    return jsonify(gpo_repository.inserir_politica(d["nome"], d.get("descricao", ""), d.get("permissoes", [])))


@gpo_bp.route("/api/gpo/politicas/<int:pid>", methods=["PUT"])
@admin_required
def api_atualizar_politica(pid):
    d = request.get_json()
    gpo_repository.atualizar_politica(pid, d.get("nome", ""), d.get("descricao", ""), d.get("permissoes", []))
    return jsonify({"ok": True})


@gpo_bp.route("/api/gpo/politicas/<int:pid>", methods=["DELETE"])
@admin_required
def api_deletar_politica(pid):
    gpo_repository.deletar_politica(pid)
    return jsonify({"ok": True})


# ── Meta ──────────────────────────────────────────────────────────────

@gpo_bp.route("/api/gpo/meta")
@admin_required
def api_gpo_meta():
    return jsonify({"roles": ROLES_SISTEMA, "permissoes": PERMISSOES_SISTEMA})
