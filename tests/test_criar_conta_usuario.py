import os
import sys
import tempfile

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from adapters.repositories.sqlite_conta_repository import SqliteContaRepository
from use_cases.criar_conta_usuario import CriarContaUsuarioUseCase


def test_cria_usuario_e_conta_no_sqlite():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "contas_test.db")
        repo = SqliteContaRepository(db_path)
        use_case = CriarContaUsuarioUseCase(repo)

        conta = use_case.executar(
            nome="Maria",
            email="maria@email.com",
            senha="senha_segura",
            saldo_inicial=150.0,
        )

        assert conta.titular == "Maria"
        assert conta.usuario_id is not None
        assert conta.id_conta is not None
        assert conta.saldo == 150.0
        assert conta.saldo_emprestimo == 0.0

        conta_db = repo.buscar("Maria")
        assert conta_db.usuario_id == conta.usuario_id
        assert conta_db.saldo == 150.0


def test_nao_permite_email_duplicado():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "contas_test.db")
        repo = SqliteContaRepository(db_path)
        use_case = CriarContaUsuarioUseCase(repo)

        use_case.executar(
            nome="Joao",
            email="joao@email.com",
            senha="hash1",
            saldo_inicial=10.0,
        )

        with pytest.raises(ValueError, match="E-mail já cadastrado"):
            use_case.executar(
                nome="Joao Souza",
                email="joao@email.com",
                senha="hash2",
                saldo_inicial=20.0,
            )
