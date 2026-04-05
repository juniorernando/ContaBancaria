import datetime
import os
from dotenv import load_dotenv
from domain.entities.transaction import Transaction
from domain.repositories.conta_repository import ContaRepository

load_dotenv()


class SacarUseCase:
    def __init__(self, repo: ContaRepository):
        self.repo = repo

    def _limite_atual(self) -> tuple[float, str]:
        hora = datetime.datetime.now().hour
        if hora >= 22 or hora < 6:
            return float(os.getenv("LIMITE_NOTURNO", 500.0)), "22h e 6h"
        return float(os.getenv("LIMITE_DIURNO", 5000.0)), "6h e 22h"

    def executar(self, titular: str, valor: float) -> None:
        if valor <= 0:
            raise ValueError("Valor de saque deve ser positivo.")

        limite, periodo = self._limite_atual()
        if valor > limite:
            raise ValueError(
                f"Entre {periodo}, o limite de saque é de R${limite:.2f}."
            )

        conta = self.repo.buscar(titular)
        if conta.saldo < valor:
            raise ValueError("Saldo insuficiente para realizar o saque.")
        conta.saldo -= valor
        self.repo.salvar(conta)
        self.repo.registrar_transacao(
            Transaction(titular, "saque", valor, f"Saque via terminal")
        )