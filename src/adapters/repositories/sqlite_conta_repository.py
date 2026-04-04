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
                CREATE TABLE IF NOT EXISTS contas (
                    titular TEXT PRIMARY KEY,
                    saldo   REAL NOT NULL DEFAULT 0.0
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

    def buscar(self, titular: str) -> Conta:
        with self._conn() as c:
            row = c.execute(
                "SELECT saldo FROM contas WHERE titular = ?", (titular,)
            ).fetchone()
            if row is None:
                c.execute(
                    "INSERT INTO contas(titular, saldo) VALUES(?, ?)", (titular, 0.0)
                )
                return Conta(titular, 0.0)
            return Conta(titular, row[0])

    def salvar(self, conta: Conta) -> None:
        with self._conn() as c:
            c.execute(
                "INSERT OR REPLACE INTO contas(titular, saldo) VALUES(?, ?)",
                (conta.titular, conta.saldo),
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
