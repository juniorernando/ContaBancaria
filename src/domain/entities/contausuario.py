class ContaUsuario:
    def __init__(
        self,
        nome: str,
        email: str,
        senha_hash: str,
        id_usuario: int | None = None,
    ):
        self.id_usuario = id_usuario
        self.nome = nome
        self.email = email
        self.senha_hash = senha_hash