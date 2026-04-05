class Conta:
    def __init__(
        self,
        titular: str,
        saldo: float = 0.0,
        saldo_emprestimo: float = 0.0,
        id_conta: int | None = None,
        usuario_id: int | None = None,
    ):
        self.id_conta = id_conta
        self.usuario_id = usuario_id
        self.titular = titular
        self.saldo = saldo
        self.saldo_emprestimo = saldo_emprestimo
