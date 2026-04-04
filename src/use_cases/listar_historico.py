from domain.repositories.conta_repository import ContaRepository


class ListarHistoricoUseCase:
    def __init__(self, repo: ContaRepository):
        self.repo = repo

    def executar(self, titular: str) -> list:
        return self.repo.listar_transacoes(titular)
