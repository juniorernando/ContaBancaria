from datetime import datetime


class Transaction:
    def __init__(self, titular: str, tipo: str, valor: float,
                 descricao: str = "", data_hora: datetime | None = None):
        self.titular = titular
        self.tipo = tipo
        self.valor = valor
        self.descricao = descricao
        self.data_hora = data_hora or datetime.now()
