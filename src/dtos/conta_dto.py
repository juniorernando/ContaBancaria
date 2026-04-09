from pydantic import BaseModel, Field

from domain.entities.conta import Conta


class ContaDTO(BaseModel):
    id_conta: int | None = None
    usuario_id: int | None = None
    titular: str
    saldo: float
    saldo_emprestimo: float

    @classmethod
    def from_entity(cls, conta: Conta) -> "ContaDTO":
        return cls(
            id_conta=conta.id_conta,
            usuario_id=conta.usuario_id,
            titular=conta.titular,
            saldo=conta.saldo,
            saldo_emprestimo=conta.saldo_emprestimo,
        )


class MovimentoRequestDTO(BaseModel):
    titular: str = Field(..., min_length=1)
    valor: float = Field(..., gt=0)


class MovimentoResponseDTO(BaseModel):
    mensagem: str
    conta: ContaDTO