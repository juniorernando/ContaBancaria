import logging
import os
import sys
from dotenv import load_dotenv
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
load_dotenv()

from core.logging_config import configure_logging

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


configure_logging()
logger = logging.getLogger(__name__)


def _cadastrar_nova_conta_se_configurada(repo: SqliteContaRepository) -> None:
    nome = os.getenv("BANCO_NOVO_NOME", "").strip()
    email = os.getenv("BANCO_NOVO_EMAIL", "").strip().lower()
    senha = os.getenv("BANCO_NOVA_SENHA", "").strip()
    saldo_raw = os.getenv("BANCO_NOVO_SALDO", "0").strip()

    # Só tenta cadastrar quando o bloco completo de credenciais for informado.
    if not (nome and email and senha):
        logger.debug("Cadastro inicial ignorado: variáveis BANCO_NOVO_* incompletas.")
        return

    try:
        saldo_inicial = float(saldo_raw)
    except ValueError:
        logger.warning("BANCO_NOVO_SALDO inválido: valor=%s. Usando 0.0.", saldo_raw)
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
        logger.info(
            "Conta criada no bootstrap. titular=%s usuario_id=%s conta_id=%s",
            conta.titular,
            conta.usuario_id,
            conta.id_conta,
        )
        print(
            f"Conta criada para {conta.titular} (usuario_id={conta.usuario_id}, conta_id={conta.id_conta})."
        )
    except ValueError as exc:
        logger.warning("Cadastro inicial não executado para email=%s: %s", email, exc)
        print(f"Cadastro inicial não executado: {exc}")


if __name__ == "__main__":
    try:
        logger.info("Inicializando aplicação ContaBancaria.")
        repo = SqliteContaRepository("data/contas.db")

        _cadastrar_nova_conta_se_configurada(repo)

        inicio = InicioInterface(repo)
        usuario, senha = inicio.escolher_fluxo_inicial()


        login = Login(repo)
        if login.sistemaLogin(usuario, senha):
            logger.info("Login autorizado para usuario=%s", usuario)
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
        else:
            logger.warning("Tentativa de login rejeitada para usuario=%s", usuario)
    except KeyboardInterrupt:
        logger.info("Aplicação encerrada pelo usuário.")
        print("\nAplicação encerrada pelo usuário.")
    except Exception:
        logger.exception("Falha não tratada na aplicação principal.")
        raise
