class Conta:
    def __init__(self, titular: str, saldo: float = 0.0, saldo_emprestimo: float = 0.0):
        self.titular = titular
        self.saldo = saldo
        self.saldo_emprestimo = saldo_emprestimo
