import os
import sys
from dotenv import load_dotenv
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
load_dotenv()

from interface.login import Login
from interface.menu import Menu
from interface.inicio import InicioInterface
from adapters.repositories.sqlite_conta_repository import SqliteContaRepository
from use_cases.criar_conta_usuario import CriarContaUsuarioUseCase
from use_cases.depositar import DepositarUseCase
from use_cases.sacar import SacarUseCase
from use_cases.ver_saldo import VerSaldoUseCase
from use_cases.emprestimo import emprestimo
from use_cases.listar_historico import ListarHistoricoUseCase


def _cadastrar_nova_conta_se_configurada(repo: SqliteContaRepository) -> None:
    nome = os.getenv("BANCO_NOVO_NOME", "").strip()
    email = os.getenv("BANCO_NOVO_EMAIL", "").strip().lower()
    senha = os.getenv("BANCO_NOVA_SENHA", "").strip()
    saldo_raw = os.getenv("BANCO_NOVO_SALDO", "0").strip()

    # Só tenta cadastrar quando o bloco completo de credenciais for informado.
    if not (nome and email and senha):
        return

    try:
        saldo_inicial = float(saldo_raw)
    except ValueError:
        print("Aviso: BANCO_NOVO_SALDO inválido. Usando saldo inicial 0.0.")
        saldo_inicial = 0.0

    uc_criar = CriarContaUsuarioUseCase(repo)
    try:
        conta = uc_criar.executar(
            nome=nome,
            email=email,
            senha=senha,
            saldo_inicial=saldo_inicial,
        )
        print(
            f"Conta criada para {conta.titular} (usuario_id={conta.usuario_id}, conta_id={conta.id_conta})."
        )
    except ValueError as exc:
        print(f"Cadastro inicial não executado: {exc}")


if __name__ == "__main__":
    repo = SqliteContaRepository("data/contas.db")

    _cadastrar_nova_conta_se_configurada(repo)

    inicio = InicioInterface(repo)
    usuario, senha = inicio.escolher_fluxo_inicial()

    login = Login(repo)
    if login.sistemaLogin(usuario, senha):
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
