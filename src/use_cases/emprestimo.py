from domain.entities.transaction import Transaction
from domain.repositories.conta_repository import ContaRepository


class emprestimo:
    def __init__(self, repo: ContaRepository):
        self.repo = repo
        

    def executar(self, titular: str, valor: float, meses: int) -> dict:
        if valor <= 0:
            raise ValueError("Valor do empréstimo deve ser positivo.")
        if meses <= 0:
            raise ValueError("Número de meses deve ser positivo.")

        conta = self.repo.buscar(titular)
        limite = 0.8 * conta.saldo

        if valor > limite:
            raise ValueError(
                f"Empréstimo negado. O valor solicitado excede 80% do saldo atual (R${limite:.2f})."
            )

        juros = self.calcular_juros(valor, meses)
        total = valor + juros
        parcela = self.calcular_parcela(valor, meses)

        conta.saldo += valor
        conta.saldo_emprestimo += total
        self.repo.salvar(conta)
        self.repo.registrar_transacao(
            Transaction(
                titular, "emprestimo", valor,
                f"Empréstimo {meses}x de R${parcela:.2f} | Total c/ juros: R${total:.2f}"
            )
        )
        return {"valor": valor, "meses": meses, "juros": juros, "total": total, "parcela": parcela}

    def calcular_juros(self, valor: float, meses: int) -> float:
        taxa_juros_mensal = 0.02
        return valor * (1 + taxa_juros_mensal) ** meses - valor
    
    def calcular_parcela(self, valor: float, meses: int) -> float:
        total_com_juros = self.calcular_juros(valor, meses) + valor
        return total_com_juros / meses
    
    def saldo_emprestimo(self, titular: str) -> float:
        conta = self.repo.buscar(titular)
        return conta.saldo_emprestimo
    
    def quitar_emprestimo(self, titular: str, valor: float) -> None:
        conta = self.repo.buscar(titular)
        if valor <= 0:
            raise ValueError("Valor de quitação deve ser positivo.")
        if conta.saldo_emprestimo == 0:
            raise ValueError("Não há empréstimo ativo para quitar.")
        if valor > conta.saldo:
            raise ValueError("Saldo insuficiente para realizar a quitação.")
        if valor > conta.saldo_emprestimo:
            raise ValueError("Valor de quitação excede o saldo devedor do empréstimo.")
        
        conta.saldo -= valor
        conta.saldo_emprestimo -= valor
        self.repo.salvar(conta)
        self.repo.registrar_transacao(
            Transaction(
                titular, "quitacao_emprestimo", valor,
                f"Quitação de empréstimo no valor de R${valor:.2f}"
            )
        )
    
