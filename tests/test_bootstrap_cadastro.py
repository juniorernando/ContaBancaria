import importlib
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from adapters.repositories.sqlite_conta_repository import SqliteContaRepository


def test_cadastro_inicial_por_variavel_de_ambiente(monkeypatch):
    lambda_module = importlib.import_module("lambda")

    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "contas_test.db")
        repo = SqliteContaRepository(db_path)

        monkeypatch.setenv("BANCO_NOVO_NOME", "Carla")
        monkeypatch.setenv("BANCO_NOVO_EMAIL", "carla@email.com")
        monkeypatch.setenv("BANCO_NOVA_SENHA", "senha_forte")
        monkeypatch.setenv("BANCO_NOVO_SALDO", "90.5")

        lambda_module._cadastrar_nova_conta_se_configurada(repo)

        conta = repo.buscar("Carla")
        assert conta.titular == "Carla"
        assert conta.usuario_id is not None
        assert conta.saldo == 90.5
