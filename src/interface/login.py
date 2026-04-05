import bcrypt
import msvcrt
import sys

from domain.repositories.conta_repository import ContaRepository


def _input_senha(prompt: str = "Digite a senha: ") -> str:
    print(prompt, end='', flush=True)
    caracteres = []
    while True:
        ch = msvcrt.getwch()
        if ch in ('\r', '\n'):      # Enter
            print()
            break
        elif ch == '\x08':          # Backspace
            if caracteres:
                caracteres.pop()
                sys.stdout.write('\b \b')
                sys.stdout.flush()
        elif ch == '\x03':          # Ctrl+C
            raise KeyboardInterrupt
        else:
            caracteres.append(ch)
            sys.stdout.write('*')
            sys.stdout.flush()
    return ''.join(caracteres)


class Login:
    def __init__(self, repo: ContaRepository):
        self.repo = repo

    def sistemaLogin(self, usuario: str, senha: str) -> bool:
        usuario_digitado = str(usuario).strip()
        senha_digitada = str(senha).strip()
        tentativas = 0

        while tentativas < 3:
            if not usuario_digitado:
                usuario_digitado = input("Digite o nome do usuario: ").strip()
            if not senha_digitada:
                senha_digitada = _input_senha("Digite a senha: ").strip()

            if len(senha_digitada) < 6:
                print("A senha deve ter pelo menos 6 caracteres.")
            elif senha_digitada == "123456":
                print("A senha não pode ser '123456'.")
            else:
                senha_hash_db = self.repo.buscar_senha_hash_por_usuario(usuario_digitado)
                if senha_hash_db and bcrypt.checkpw(
                    senha_digitada.encode("utf-8"),
                    senha_hash_db.encode("utf-8"),
                ):
                    print("Entrada autorizada")
                    return True

            tentativas += 1
            usuario_digitado = ""
            senha_digitada = ""
            print(f"Usuario invalido. Tentativas restantes: {3 - tentativas}")

        print("Acesso bloqueado")
        return False