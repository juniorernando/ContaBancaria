import bcrypt

from domain.entities.conta import Conta
from domain.repositories.conta_repository import ContaRepository


class CriarContaUsuarioUseCase:
    def __init__(self, repo: ContaRepository):
        self.repo = repo

    def executar(
        self,
        nome: str,
        email: str,
        senha: str,
        saldo_inicial: float = 0.0,
    ) -> Conta:
        nome = nome.strip()
        email = email.strip().lower()
        senha = senha.strip()

        if not nome:
            raise ValueError("Nome é obrigatório.")
        if not email:
            raise ValueError("E-mail é obrigatório.")
        if not senha:
            raise ValueError("Senha é obrigatória.")

        senha_hash = bcrypt.hashpw(
            senha.encode("utf-8"),
            bcrypt.gensalt(),
        ).decode("utf-8")

        return self.repo.criar_conta_usuario(
            nome=nome,
            email=email,
            senha_hash=senha_hash,
            saldo_inicial=saldo_inicial,
        )
