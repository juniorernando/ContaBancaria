import os
import sqlite3
from datetime import datetime

from domain.entities.conta import Conta
from domain.entities.transaction import Transaction
from domain.repositories.conta_repository import ContaRepository


class SqliteContaRepository(ContaRepository):
    def __init__(self, db_path: str = "data/contas.db"):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self._init_db()

    def _conn(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _init_db(self) -> None:
        with self._conn() as c:
            c.execute("""
                CREATE TABLE IF NOT EXISTS usuarios (
                    id         INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome       TEXT    NOT NULL,
                    email      TEXT    NOT NULL UNIQUE,
                    senha_hash TEXT    NOT NULL
                )
            """)
            c.execute("""
                CREATE TABLE IF NOT EXISTS contas (
                    titular          TEXT PRIMARY KEY,
                    saldo            REAL    NOT NULL DEFAULT 0.0,
                    saldo_emprestimo REAL    NOT NULL DEFAULT 0.0,
                    usuario_id       INTEGER UNIQUE,
                    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
                )
            """)
            c.execute("""
                CREATE TABLE IF NOT EXISTS transacoes (
                    id        INTEGER PRIMARY KEY AUTOINCREMENT,
                    titular   TEXT    NOT NULL,
                    tipo      TEXT    NOT NULL,
                    valor     REAL    NOT NULL,
                    data_hora TEXT    NOT NULL,
                    descricao TEXT    DEFAULT ''
                )
            """)
            self._migrar_tabela_contas(c)

    def _migrar_tabela_contas(self, conn: sqlite3.Connection) -> None:
        columns = {
            row[1] for row in conn.execute("PRAGMA table_info(contas)").fetchall()
        }
        if "saldo_emprestimo" not in columns:
            conn.execute(
                "ALTER TABLE contas ADD COLUMN saldo_emprestimo REAL NOT NULL DEFAULT 0.0"
            )
        if "usuario_id" not in columns:
            conn.execute("ALTER TABLE contas ADD COLUMN usuario_id INTEGER")

    def criar_conta_usuario(
        self,
        nome: str,
        email: str,
        senha_hash: str,
        saldo_inicial: float = 0.0,
    ) -> Conta:
        if saldo_inicial < 0:
            raise ValueError("Saldo inicial não pode ser negativo.")

        try:
            with self._conn() as c:
                cursor = c.execute(
                    "INSERT INTO usuarios(nome, email, senha_hash) VALUES(?, ?, ?)",
                    (nome, email, senha_hash),
                )
                usuario_id = cursor.lastrowid

                cursor = c.execute(
                    """
                    INSERT INTO contas(titular, saldo, saldo_emprestimo, usuario_id)
                    VALUES(?, ?, ?, ?)
                    """,
                    (nome, saldo_inicial, 0.0, usuario_id),
                )
                conta_id = cursor.lastrowid
        except sqlite3.IntegrityError as exc:
            mensagem = str(exc).lower()
            if "usuarios.email" in mensagem or "email" in mensagem:
                raise ValueError("E-mail já cadastrado.") from exc
            if "contas.titular" in mensagem or "titular" in mensagem:
                raise ValueError("Já existe uma conta com esse titular.") from exc
            raise ValueError("Não foi possível criar a conta do usuário.") from exc

        return Conta(
            titular=nome,
            saldo=saldo_inicial,
            saldo_emprestimo=0.0,
            id_conta=conta_id,
            usuario_id=usuario_id,
        )

    def buscar_senha_hash_por_usuario(self, nome: str) -> str | None:
        with self._conn() as c:
            row = c.execute(
                "SELECT senha_hash FROM usuarios WHERE nome = ?",
                (nome,),
            ).fetchone()
        return row[0] if row else None

    def buscar(self, titular: str) -> Conta:
        with self._conn() as c:
            row = c.execute(
                "SELECT rowid, saldo, saldo_emprestimo, usuario_id FROM contas WHERE titular = ?",
                (titular,),
            ).fetchone()
            if row is None:
                c.execute(
                    "INSERT INTO contas(titular, saldo, saldo_emprestimo) VALUES(?, ?, ?)",
                    (titular, 0.0, 0.0),
                )
                return Conta(titular, 0.0)
            return Conta(
                titular=titular,
                saldo=row[1],
                saldo_emprestimo=row[2],
                id_conta=row[0],
                usuario_id=row[3],
            )

    def salvar(self, conta: Conta) -> None:
        with self._conn() as c:
            cursor = c.execute(
                """
                UPDATE contas
                SET saldo = ?, saldo_emprestimo = ?, usuario_id = COALESCE(?, usuario_id)
                WHERE titular = ?
                """,
                (conta.saldo, conta.saldo_emprestimo, conta.usuario_id, conta.titular),
            )
            if cursor.rowcount == 0:
                c.execute(
                    """
                    INSERT INTO contas(titular, saldo, saldo_emprestimo, usuario_id)
                    VALUES(?, ?, ?, ?)
                    """,
                    (
                        conta.titular,
                        conta.saldo,
                        conta.saldo_emprestimo,
                        conta.usuario_id,
                    ),
                )

    def registrar_transacao(self, trans: Transaction) -> None:
        with self._conn() as c:
            c.execute(
                "INSERT INTO transacoes(titular, tipo, valor, data_hora, descricao) VALUES(?, ?, ?, ?, ?)",
                (trans.titular, trans.tipo, trans.valor,
                 trans.data_hora.isoformat(), trans.descricao),
            )

    def listar_transacoes(self, titular: str) -> list[Transaction]:
        with self._conn() as c:
            rows = c.execute(
                "SELECT tipo, valor, data_hora, descricao FROM transacoes "
                "WHERE titular = ? ORDER BY data_hora DESC",
                (titular,),
            ).fetchall()
        return [
            Transaction(titular, r[0], r[1], r[3], datetime.fromisoformat(r[2]))
            for r in rows
        ]
