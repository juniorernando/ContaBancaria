import os
import sys
from typing import Annotated

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
load_dotenv()

from adapters.repositories.sqlite_conta_repository import SqliteContaRepository
from use_cases.depositar import DepositarUseCase
from use_cases.sacar import SacarUseCase
from use_cases.ver_saldo import VerSaldoUseCase


class MovimentoRequest(BaseModel):
    titular: str = Field(..., min_length=1)
    valor: float = Field(..., gt=0)


class SaldoResponse(BaseModel):
    titular: str
    saldo: float


class MovimentoResponse(BaseModel):
    mensagem: str
    titular: str
    saldo: float


def create_app(repo: SqliteContaRepository | None = None) -> FastAPI:
    repositorio = repo or SqliteContaRepository("data/contas.db")

    depositar_uc = DepositarUseCase(repositorio)
    sacar_uc = SacarUseCase(repositorio)
    ver_saldo_uc = VerSaldoUseCase(repositorio)

    app = FastAPI(title="ContaBancaria API", version="1.0.0")

    @app.post("/deposito", response_model=MovimentoResponse)
    def depositar(payload: MovimentoRequest) -> MovimentoResponse:
        try:
            depositar_uc.executar(payload.titular, payload.valor)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

        saldo = ver_saldo_uc.executar(payload.titular)
        return MovimentoResponse(
            mensagem="Depósito realizado com sucesso.",
            titular=payload.titular,
            saldo=saldo,
        )

    @app.post("/saque", response_model=MovimentoResponse)
    def sacar(payload: MovimentoRequest) -> MovimentoResponse:
        try:
            sacar_uc.executar(payload.titular, payload.valor)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

        saldo = ver_saldo_uc.executar(payload.titular)
        return MovimentoResponse(
            mensagem="Saque realizado com sucesso.",
            titular=payload.titular,
            saldo=saldo,
        )

    @app.get("/saldo", response_model=SaldoResponse)
    def consultar_saldo(
        titular: Annotated[str, Query(min_length=1)]
    ) -> SaldoResponse:
        saldo = ver_saldo_uc.executar(titular)
        return SaldoResponse(titular=titular, saldo=saldo)

    return app


app = create_app()