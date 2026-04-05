from adapters.repositories.sqlite_conta_repository import SqliteContaRepository
from interface.login import _input_senha
from use_cases.criar_conta_usuario import CriarContaUsuarioUseCase


class InicioInterface:
    def __init__(self, repo: SqliteContaRepository):
        self.repo = repo

    def escolher_fluxo_inicial(self) -> tuple[str, str]:
        while True:
            print("\n=== Acesso Inicial ===")
            print("1. Usuario existente")
            print("2. Novo usuario")
            print("3. Sair")

            opcao = input("Escolha uma opcao: ").strip()
            if opcao == "1":
                return self._fluxo_usuario_existente()
            if opcao == "2":
                return self._fluxo_novo_usuario()
            if opcao == "3":
                raise SystemExit("Aplicacao encerrada.")
            print("Opcao invalida. Tente novamente.")

    def _fluxo_usuario_existente(self) -> tuple[str, str]:
        print("\n=== Login de Usuario Existente ===")
        usuario = input("Digite o nome do usuario: ").strip()
        senha = _input_senha("Digite a senha: ").strip()
        return usuario, senha

    def _fluxo_novo_usuario(self) -> tuple[str, str]:
        print("\n=== Cadastro de Novo Usuario ===")
        nome = input("Nome: ").strip()
        email = input("E-mail: ").strip().lower()
        senha = _input_senha("Senha: ").strip()
        confirmar_senha = _input_senha("Confirme a senha: ").strip()
        deposito_raw = input("Deposito inicial (Enter para 0): ").strip()

        if senha != confirmar_senha:
            print("As senhas nao coincidem.")
            return self.escolher_fluxo_inicial()

        try:
            saldo_inicial = float(deposito_raw) if deposito_raw else 0.0
        except ValueError:
            print("Deposito inicial invalido. Usando 0.0.")
            saldo_inicial = 0.0

        uc = CriarContaUsuarioUseCase(self.repo)
        try:
            conta = uc.executar(
                nome=nome,
                email=email,
                senha=senha,
                saldo_inicial=saldo_inicial,
            )
        except ValueError as exc:
            print(f"Falha ao cadastrar usuario: {exc}")
            return self.escolher_fluxo_inicial()

        print(
            f"Cadastro realizado para {conta.titular} "
            f"(usuario_id={conta.usuario_id}, conta_id={conta.id_conta})."
        )
        return nome, senha