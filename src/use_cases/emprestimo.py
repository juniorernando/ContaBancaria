from use_cases.depositar import DepositarUseCase
from use_cases.ver_saldo import VerSaldoUseCase


class emprestimo:
    def __init__(self, depositar_uc: DepositarUseCase, ver_saldo_uc: VerSaldoUseCase):
        self.depositar_uc = depositar_uc
        self.ver_saldo_uc = ver_saldo_uc

    def executar(self, titular: str, valor: float):
        if valor <= 0:
            raise ValueError("Valor do empréstimo deve ser positivo.")
        
        saldo_atual = self.ver_saldo_uc.executar(titular)
        limite = 0.8 * saldo_atual

        if valor > limite:
            raise ValueError(f"Empréstimo negado. O valor solicitado excede 80% do saldo atual (R${limite:.2f}).")
        self.depositar_uc.executar(titular, valor)