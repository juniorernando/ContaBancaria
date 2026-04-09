import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from adapters.repositories.sqlite_conta_repository import SqliteContaRepository
from interface.login import Login
from use_cases.criar_conta_usuario import CriarContaUsuarioUseCase


def test_login_com_hash_bcrypt_funciona():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "contas_test.db")
        repo = SqliteContaRepository(db_path)
        CriarContaUsuarioUseCase(repo).executar(
            nome="junior",
            email="junior@email.com",
            senha="senha_segura",
            saldo_inicial=0.0,
        )

        login = Login(repo)

        assert login.sistemaLogin("junior", "senha_segura") is True


def test_login_legado_migra_senha_texto_puro_para_bcrypt():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "contas_test.db")
        repo = SqliteContaRepository(db_path)
        repo.criar_conta_usuario(
            nome="junior",
            email="junior@email.com",
            senha_hash="senha_legada",
            saldo_inicial=0.0,
        )

        assert repo.buscar_senha_hash_por_usuario("junior") == "senha_legada"

        login = Login(repo)

        assert login.sistemaLogin("junior", "senha_legada") is True

        senha_armazenada = repo.buscar_senha_hash_por_usuario("junior")
        assert senha_armazenada is not None
        assert senha_armazenada != "senha_legada"
        assert senha_armazenada.startswith("$2")
