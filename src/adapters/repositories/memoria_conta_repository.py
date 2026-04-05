from domain.entities.conta import Conta
from domain.entities.transaction import Transaction
from domain.repositories.conta_repository import ContaRepository


class MemoriaContaRepository(ContaRepository):
    # Repositório em memória para contas bancárias
    def __init__(self):
        self._contas: dict[str, Conta] = {}
        self._transacoes: list[Transaction] = []
        self._usuarios_por_email: dict[str, dict] = {}
        self._seq_usuario = 1
        self._seq_conta = 1

    def criar_conta_usuario(
        self,
        nome: str,
        email: str,
        senha_hash: str,
        saldo_inicial: float = 0.0,
    ) -> Conta:
        if saldo_inicial < 0:
            raise ValueError("Saldo inicial não pode ser negativo.")
        if email in self._usuarios_por_email:
            raise ValueError("E-mail já cadastrado.")
        if nome in self._contas:
            raise ValueError("Já existe uma conta com esse titular.")

        usuario_id = self._seq_usuario
        self._seq_usuario += 1
        conta_id = self._seq_conta
        self._seq_conta += 1

        self._usuarios_por_email[email] = {
            "id_usuario": usuario_id,
            "nome": nome,
            "senha_hash": senha_hash,
        }

        conta = Conta(
            titular=nome,
            saldo=saldo_inicial,
            saldo_emprestimo=0.0,
            id_conta=conta_id,
            usuario_id=usuario_id,
        )
        self._contas[nome] = conta
        return conta

    def buscar(self, titular: str) -> Conta:
        if titular not in self._contas:
            self._contas[titular] = Conta(titular)
        return self._contas[titular]

    def salvar(self, conta: Conta) -> None:
        self._contas[conta.titular] = conta

    def registrar_transacao(self, trans: Transaction) -> None:
        self._transacoes.append(trans)

    def listar_transacoes(self, titular: str) -> list[Transaction]:
        return [t for t in reversed(self._transacoes) if t.titular == titular]
