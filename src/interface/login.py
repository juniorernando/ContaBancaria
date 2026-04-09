import bcrypt
import logging
import msvcrt
import sys

from domain.repositories.conta_repository import ContaRepository


logger = logging.getLogger(__name__)


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

    def _validar_senha(self, senha_digitada: str, senha_hash_db: str, usuario: str) -> bool:
        try:
            return bcrypt.checkpw(
                senha_digitada.encode("utf-8"),
                senha_hash_db.encode("utf-8"),
            )
        except ValueError:
            # Compatibilidade com usuários antigos cuja senha ainda está salva em texto puro.
            if senha_digitada != senha_hash_db:
                logger.warning("Senha em formato legado inválida para usuario=%s", usuario)
                return False

            novo_hash = bcrypt.hashpw(
                senha_digitada.encode("utf-8"),
                bcrypt.gensalt(),
            ).decode("utf-8")
            self.repo.atualizar_senha_hash_usuario(usuario, novo_hash)
            logger.info("Senha legado migrada para bcrypt. usuario=%s", usuario)
            return True

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
                logger.warning("Login rejeitado por senha curta. usuario=%s", usuario_digitado)
                print("A senha deve ter pelo menos 6 caracteres.")
            elif senha_digitada == "123456":
                logger.warning("Login rejeitado por senha proibida. usuario=%s", usuario_digitado)
                print("A senha não pode ser '123456'.")
            else:
                senha_hash_db = self.repo.buscar_senha_hash_por_usuario(usuario_digitado)
                if not senha_hash_db:
                    logger.warning("Login falhou: usuário não encontrado. usuario=%s", usuario_digitado)
                if senha_hash_db and self._validar_senha(
                    senha_digitada,
                    senha_hash_db,
                    usuario_digitado,
                ):
                    logger.info("Login bem-sucedido. usuario=%s", usuario_digitado)
                    print("Entrada autorizada")
                    return True

            tentativas += 1
            usuario_digitado = ""
            senha_digitada = ""
            logger.warning("Tentativa de login inválida. tentativas_restantes=%s", 3 - tentativas)
            print(f"Usuario invalido. Tentativas restantes: {3 - tentativas}")

        logger.error("Acesso bloqueado após exceder tentativas de login.")
        print("Acesso bloqueado")
        return False