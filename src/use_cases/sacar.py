import datetime
from domain.repositories.conta_repository import ContaRepository
import os
from dotenv import load_dotenv
load_dotenv()



class SacarUseCase:
    def __init__(self, repo: ContaRepository):
        self.repo = repo

    # Limite de saque: R$ 500,00 entre 6h e 22h, e R$ 100,00 entre 22h e 6h
    def _limite_atual(self) -> float:
        hora = datetime.datetime.now().hour
        if hora >= 22 or hora < 6:
            return float(os.getenv("LIMITE_NOTURNO")), "Entre 22h e 6h, o limite é de R${:.2f}."
        return float(os.getenv("LIMITE_DIURNO")), "Entre 6h e 22h, o limite é de R${:.2f}."
    
    def executar(self, titular: str, valor: float) -> bool:
        if valor <= 0:
            raise ValueError("Valor de saque deve ser positivo.")
        
        # Verificar limite de saque
        limite, periodo = self._limite_atual()
        if valor > limite:
            raise ValueError(f"Valor de saque excede o limite permitido. {periodo.format(limite)}")
            
        
        conta = self.repo.buscar(titular)
        if conta.saldo < valor:
            raise ValueError("Saldo insuficiente para realizar o saque.")
        conta.saldo -= valor
        self.repo.salvar(conta)
        return True

     
        