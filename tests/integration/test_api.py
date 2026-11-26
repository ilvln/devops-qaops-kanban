"""Testes de integracao/API: requisicoes HTTP reais contra a aplicacao Flask."""

import pytest

from app.api import create_app


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    return app.test_client()


def _criar(client, titulo="Tarefa", prioridade="MEDIA"):
    return client.post("/api/cards", json={"titulo": titulo, "prioridade": prioridade})


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "ok"


def test_pagina_web(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"Kanban" in resp.data


def test_criar_e_listar(client):
    resp = _criar(client, "Estudar", "ALTA")
    assert resp.status_code == 201
    esperado = {"id": 1, "titulo": "Estudar", "prioridade": "ALTA", "coluna": "A_FAZER"}
    assert resp.get_json() == esperado
    assert len(client.get("/api/cards").get_json()) == 1


def test_mover_e_resumo(client):
    _criar(client)
    resp = client.post("/api/cards/1/mover", json={"coluna": "FAZENDO"})
    assert resp.status_code == 200
    assert resp.get_json()["coluna"] == "FAZENDO"
    assert client.get("/api/resumo").get_json()["wip_livre"] == 2


def test_limite_wip_via_api(client):
    for i in range(1, 5):
        _criar(client, f"t{i}")
    for i in range(1, 4):
        assert client.post(f"/api/cards/{i}/mover", json={"coluna": "FAZENDO"}).status_code == 200
    resp = client.post("/api/cards/4/mover", json={"coluna": "FAZENDO"})
    assert resp.status_code == 409
    assert "WIP" in resp.get_json()["erro"]


def test_pular_coluna_retorna_409(client):
    _criar(client)
    assert client.post("/api/cards/1/mover", json={"coluna": "FEITO"}).status_code == 409


@pytest.mark.parametrize(
    "payload",
    [
        {"titulo": ""},
        {"titulo": "x" * 101},
        {"prioridade": "ALTA"},
        {"titulo": "t", "prioridade": "X"},
    ],
)
def test_criar_dados_invalidos(client, payload):
    resp = client.post("/api/cards", json=payload)
    assert resp.status_code == 422
    assert "erro" in resp.get_json()


def test_corpo_nao_json(client):
    resp = client.post("/api/cards", data="texto", content_type="text/plain")
    assert resp.status_code == 400


def test_filtro_coluna_invalido(client):
    assert client.get("/api/cards?coluna=XYZ").status_code == 422


def test_card_inexistente(client):
    assert client.post("/api/cards/9/mover", json={"coluna": "FAZENDO"}).status_code == 404
    assert client.delete("/api/cards/9").status_code == 404


def test_remover(client):
    _criar(client)
    assert client.delete("/api/cards/1").status_code == 204
    assert client.get("/api/cards").get_json() == []
