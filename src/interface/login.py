import msvcrt
import sys


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
    def sistemaLogin(self, usuario: str, senha: str) -> bool:
        senha = str(senha).strip()

        if len(senha) < 6:
            print("A senha deve ter pelo menos 6 caracteres.")
            return False
        if senha == "123456":
            print("A senha não pode ser '123456'.")
            return False

        tentativas = 0
        while tentativas < 3:
            usuario_digitado = input("Digite o nome do usuario: ")
            senha_digitada = _input_senha("Digite a senha: ")

            if usuario_digitado == usuario and senha_digitada == senha:
                print("Entrada autorizada")
                return True

            tentativas += 1
            print(f"Usuario invalido. Tentativas restantes: {3 - tentativas}")

        print("Acesso bloqueado")
        return False