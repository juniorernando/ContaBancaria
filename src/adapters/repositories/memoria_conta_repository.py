from domain.entities.conta import Conta
from domain.repositories.conta_repository import ContaRepository


class MemoriaContaRepository(ContaRepository):
    # Repositório em memória para contas bancárias
    def __init__(self):
        self._contas: dict[str, Conta] = {}

    def buscar(self, titular: str) -> Conta:
        if titular not in self._contas:
            self._contas[titular] = Conta(titular)
        return self._contas[titular]

    def salvar(self, conta: Conta) -> None:
        self._contas[conta.titular] = conta
