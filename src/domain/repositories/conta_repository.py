from abc import ABC, abstractmethod
from domain.entities.conta import Conta


class ContaRepository(ABC):
    @abstractmethod
    def buscar(self, titular: str) -> Conta: ...

    @abstractmethod
    def salvar(self, conta: Conta) -> None: ...
