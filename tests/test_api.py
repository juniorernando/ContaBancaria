import os
import sys
import tempfile

from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from api import create_app
from adapters.repositories.sqlite_conta_repository import SqliteContaRepository
from use_cases.criar_conta_usuario import CriarContaUsuarioUseCase


def _make_client():
    tmpdir = tempfile.TemporaryDirectory()
    db_path = os.path.join(tmpdir.name, "contas_test.db")
    repo = SqliteContaRepository(db_path)
    app = create_app(repo)
    client = TestClient(app)
    return tmpdir, repo, client


def test_post_deposito_retorna_novo_saldo():
    tmpdir, repo, client = _make_client()
    try:
        CriarContaUsuarioUseCase(repo).executar(
            nome="Maria",
            email="maria@email.com",
            senha="senha_segura",
            saldo_inicial=100.0,
        )

        response = client.post(
            "/deposito",
            json={"titular": "Maria", "valor": 50.0},
        )

        assert response.status_code == 200
        assert response.json() == {
            "mensagem": "Depósito realizado com sucesso.",
            "titular": "Maria",
            "saldo": 150.0,
        }
    finally:
        tmpdir.cleanup()


def test_post_saque_retorna_novo_saldo():
    tmpdir, repo, client = _make_client()
    try:
        CriarContaUsuarioUseCase(repo).executar(
            nome="Joao",
            email="joao@email.com",
            senha="senha_segura",
            saldo_inicial=200.0,
        )

        response = client.post(
            "/saque",
            json={"titular": "Joao", "valor": 50.0},
        )

        assert response.status_code == 200
        assert response.json() == {
            "mensagem": "Saque realizado com sucesso.",
            "titular": "Joao",
            "saldo": 150.0,
        }
    finally:
        tmpdir.cleanup()


def test_get_saldo_retorna_saldo_atual():
    tmpdir, repo, client = _make_client()
    try:
        CriarContaUsuarioUseCase(repo).executar(
            nome="Ana",
            email="ana@email.com",
            senha="senha_segura",
            saldo_inicial=300.0,
        )

        response = client.get("/saldo", params={"titular": "Ana"})

        assert response.status_code == 200
        assert response.json() == {
            "titular": "Ana",
            "saldo": 300.0,
        }
    finally:
        tmpdir.cleanup()


def test_post_saque_retorna_400_quando_saldo_insuficiente():
    tmpdir, repo, client = _make_client()
    try:
        CriarContaUsuarioUseCase(repo).executar(
            nome="Paulo",
            email="paulo@email.com",
            senha="senha_segura",
            saldo_inicial=20.0,
        )

        response = client.post(
            "/saque",
            json={"titular": "Paulo", "valor": 50.0},
        )

        assert response.status_code == 400
        assert response.json()["detail"] == "Saldo insuficiente para realizar o saque."
    finally:
        tmpdir.cleanup()