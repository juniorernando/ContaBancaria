import logging
import os
import sys
from typing import Annotated

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
load_dotenv()

from adapters.repositories.sqlite_conta_repository import SqliteContaRepository
from core.logging_config import configure_logging
from dtos.conta_dto import ContaDTO, MovimentoRequestDTO, MovimentoResponseDTO
from use_cases.depositar import DepositarUseCase
from use_cases.sacar import SacarUseCase
from use_cases.ver_saldo import VerSaldoUseCase


configure_logging()
logger = logging.getLogger(__name__)


def create_app(repo: SqliteContaRepository | None = None) -> FastAPI:
    repositorio = repo or SqliteContaRepository("data/contas.db")

    depositar_uc = DepositarUseCase(repositorio)
    sacar_uc = SacarUseCase(repositorio)
    ver_saldo_uc = VerSaldoUseCase(repositorio)

    app = FastAPI(title="ContaBancaria API", version="1.0.0")

    @app.post("/deposito", response_model=MovimentoResponseDTO)
    def depositar(payload: MovimentoRequestDTO) -> MovimentoResponseDTO:
        logger.info("Requisição de depósito recebida. titular=%s valor=%.2f", payload.titular, payload.valor)
        try:
            depositar_uc.executar(payload.titular, payload.valor)
        except ValueError as exc:
            logger.warning("Depósito rejeitado. titular=%s motivo=%s", payload.titular, exc)
            raise HTTPException(status_code=400, detail=str(exc)) from exc

        conta = repositorio.buscar(payload.titular)
        logger.info("Depósito concluído. titular=%s saldo=%.2f", conta.titular, conta.saldo)
        return MovimentoResponseDTO(
            mensagem="Depósito realizado com sucesso.",
            conta=ContaDTO.from_entity(conta),
        )

    @app.post("/saque", response_model=MovimentoResponseDTO)
    def sacar(payload: MovimentoRequestDTO) -> MovimentoResponseDTO:
        logger.info("Requisição de saque recebida. titular=%s valor=%.2f", payload.titular, payload.valor)
        try:
            sacar_uc.executar(payload.titular, payload.valor)
        except ValueError as exc:
            logger.warning("Saque rejeitado. titular=%s motivo=%s", payload.titular, exc)
            raise HTTPException(status_code=400, detail=str(exc)) from exc

        conta = repositorio.buscar(payload.titular)
        logger.info("Saque concluído. titular=%s saldo=%.2f", conta.titular, conta.saldo)
        return MovimentoResponseDTO(
            mensagem="Saque realizado com sucesso.",
            conta=ContaDTO.from_entity(conta),
        )

    @app.get("/saldo", response_model=ContaDTO)
    def consultar_saldo(
        titular: Annotated[str, Query(min_length=1)]
    ) -> ContaDTO:
        logger.info("Consulta de saldo recebida. titular=%s", titular)
        ver_saldo_uc.executar(titular)
        conta = repositorio.buscar(titular)
        logger.info("Saldo consultado. titular=%s saldo=%.2f", conta.titular, conta.saldo)
        return ContaDTO.from_entity(conta)

    return app


app = create_app()