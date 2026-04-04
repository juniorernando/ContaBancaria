from domain.entities.transaction import Transaction
from domain.repositories.conta_repository import ContaRepository


class DepositarUseCase:
    def __init__(self, repo: ContaRepository):
        self.repo = repo

    def executar(self, titular: str, valor: float) -> None:
        if valor <= 0:
            raise ValueError("Valor de depósito deve ser positivo.")
        conta = self.repo.buscar(titular)
        conta.saldo += valor
        self.repo.salvar(conta)
        self.repo.registrar_transacao(
            Transaction(titular, "deposito", valor, "Depósito via terminal")
        )
