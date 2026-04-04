import os
import sys
from dotenv import load_dotenv
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
load_dotenv()

from interface.login import Login
from interface.menu import Menu
from adapters.repositories.sqlite_conta_repository import SqliteContaRepository
from use_cases.depositar import DepositarUseCase
from use_cases.sacar import SacarUseCase
from use_cases.ver_saldo import VerSaldoUseCase
from use_cases.emprestimo import emprestimo
from use_cases.listar_historico import ListarHistoricoUseCase


if __name__ == "__main__":
    usuario = os.getenv("BANCO_USUARIO")
    senha = os.getenv("BANCO_SENHA")

    login = Login()
    if login.sistemaLogin(usuario, senha):
        repo = SqliteContaRepository("data/contas.db")
        menu = Menu(
            titular=usuario,
            depositar_uc=DepositarUseCase(repo),
            sacar_uc=SacarUseCase(repo),
            ver_saldo_uc=VerSaldoUseCase(repo),
            emprestimo_uc=emprestimo(repo),
            historico_uc=ListarHistoricoUseCase(repo),
        )
        while True:
            menu.exibir()
            opcao = input("Escolha uma opção: ")
            if menu.escolher_opcao(opcao):
                break
