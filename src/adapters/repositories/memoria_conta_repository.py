from domain.entities.conta import Conta
from domain.entities.transaction import Transaction
from domain.repositories.conta_repository import ContaRepository


class MemoriaContaRepository(ContaRepository):
    # Repositório em memória para contas bancárias
    def __init__(self):
        self._contas: dict[str, Conta] = {}
        self._transacoes: list[Transaction] = []

    def buscar(self, titular: str) -> Conta:
        if titular not in self._contas:
            self._contas[titular] = Conta(titular)
        return self._contas[titular]

    def salvar(self, conta: Conta) -> None:
        self._contas[conta.titular] = conta

    def registrar_transacao(self, trans: Transaction) -> None:
        self._transacoes.append(trans)

    def listar_transacoes(self, titular: str) -> list[Transaction]:
        return [t for t in reversed(self._transacoes) if t.titular == titular]
