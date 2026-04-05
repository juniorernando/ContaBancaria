from abc import ABC, abstractmethod
from domain.entities.conta import Conta
from domain.entities.transaction import Transaction


class ContaRepository(ABC):
    @abstractmethod
    def criar_conta_usuario(
        self,
        nome: str,
        email: str,
        senha_hash: str,
        saldo_inicial: float = 0.0,
    ) -> Conta: ...

    @abstractmethod
    def buscar(self, titular: str) -> Conta: ...

    @abstractmethod
    def salvar(self, conta: Conta) -> None: ...

    @abstractmethod
    def registrar_transacao(self, trans: Transaction) -> None: ...

    @abstractmethod
    def listar_transacoes(self, titular: str) -> list[Transaction]: ...
