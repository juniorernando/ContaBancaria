from domain.repositories.conta_repository import ContaRepository


class VerSaldoUseCase:
    def __init__(self, repo: ContaRepository):
        self.repo = repo

    def executar(self, titular: str) -> float:
        conta = self.repo.buscar(titular)
        return conta.saldo
