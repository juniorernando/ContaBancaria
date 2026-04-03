import datetime

from use_cases.depositar import DepositarUseCase
from use_cases.emprestimo import emprestimo
from use_cases.sacar import SacarUseCase
from use_cases.ver_saldo import VerSaldoUseCase


class Menu:
    def __init__(self, titular: str, depositar_uc: DepositarUseCase,
                 sacar_uc: SacarUseCase, ver_saldo_uc: VerSaldoUseCase, emprestimo_uc: emprestimo):
        self.titular = titular
        self.depositar_uc = depositar_uc
        self.sacar_uc = sacar_uc
        self.ver_saldo_uc = ver_saldo_uc
        self.emprestimocase = emprestimo_uc

    def saldacao(self):
        hora = datetime.datetime.now().hour
        if 6 <= hora < 12:
            periodo = "Bom dia"
        elif 12 <= hora < 18:
            periodo = "Boa tarde"
        else:
            periodo = "Boa noite"
        print(f"Olá, {periodo}! {self.titular}, seja bem-vindo ao Banco Itaú.")
        print()

    def exibir(self):
        self.saldacao()
        print("=== Menu ===")
        print()
        print("1. Depositar")
        print("2. Sacar")
        print("3. Ver Saldo")
        print("5. Empréstimo")
        print("6. Sair")


    def escolher_opcao(self, opcao: str) -> bool:
        if opcao == '1':
            valor = float(input("Digite o valor a ser depositado: "))
            if valor == 0:
                print("Valor de depósito não pode ser zero.")
            else:
                try:
                    self.depositar_uc.executar(self.titular, valor)
                    print(f"Depósito de R${valor:.2f} realizado com sucesso.")
                except ValueError as e:
                    print(f"Erro: {e}")
        elif opcao == '2':
            valor = float(input("Digite o valor a ser sacado: "))
            try:
                self.sacar_uc.executar(self.titular, valor)
                print(f"Saque de R${valor:.2f} realizado com sucesso.")
            except ValueError as e:
                print(f"Erro: {e}")
        elif opcao == '3':
            saldo = self.ver_saldo_uc.executar(self.titular)
            print(f"Saldo atual: R${saldo:.2f}")
        elif opcao == '4':
            print("Saindo do menu. Obrigado por usar nossos serviços!")
            return True
        elif opcao == '5':
            valor = float(input("Digite o valor do empréstimo: "))
            try:
                self.emprestimocase.executar(self.titular, valor)
                print(f"Empréstimo de R${valor:.2f} realizado com sucesso.")
            except ValueError as e:
                print(f"Erro: {e}")
            
        else:
            print("Opção inválida. Por favor, escolha uma opção válida.")
        return False
