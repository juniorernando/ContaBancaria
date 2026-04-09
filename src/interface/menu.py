import datetime

from use_cases.depositar import DepositarUseCase
from use_cases.emprestimo import emprestimo
from use_cases.listar_historico import ListarHistoricoUseCase
from use_cases.sacar import SacarUseCase
from use_cases.ver_saldo import VerSaldoUseCase


class Menu:
    def __init__(self, titular: str, depositar_uc: DepositarUseCase,
                 sacar_uc: SacarUseCase, ver_saldo_uc: VerSaldoUseCase,
                 emprestimo_uc: emprestimo, historico_uc: ListarHistoricoUseCase):
        self.titular = titular
        self.depositar_uc = depositar_uc
        self.sacar_uc = sacar_uc
        self.ver_saldo_uc = ver_saldo_uc
        self.emprestimocase = emprestimo_uc
        self.historico_uc = historico_uc

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
        print()
        self.saldacao()
        print("=== Menu ===")
        print()
        print("1. Depositar")
        print("2. Sacar")
        print("3. Ver Saldo")
        print("4. Histórico de Transações")
        print("5. Empréstimo")
        print("6. Sair")
        print()

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
            transacoes = self.historico_uc.executar(self.titular)
            if not transacoes:
                print("Nenhuma transação encontrada.")
            else:
                print("\n=== Histórico de Transações ===")
                for t in transacoes:
                    print(f"[{t.data_hora.strftime('%d/%m/%Y %H:%M:%S')}] "
                          f"{t.tipo.upper():<12} R${t.valor:>10.2f}  {t.descricao}")
                print()
        elif opcao == '5':
            self._menu_emprestimo()
        elif opcao == '6':
            print("Saindo do menu. Obrigado por usar nossos serviços!")
            return True

        else:
            print("Opção inválida. Por favor, escolha uma opção válida.")
        return False

    def _menu_emprestimo(self):
        saldo_devedor = self.emprestimocase.saldo_emprestimo(self.titular)
        saldo_conta = self.ver_saldo_uc.executar(self.titular)
        limite = 0.8 * saldo_conta

        print()
        print("=== Empréstimo ===")
        print(f"  Saldo disponível  : R${saldo_conta:.2f}")
        print(f"  Limite (80%)      : R${limite:.2f}")
        print(f"  Saldo devedor     : R${saldo_devedor:.2f}")
        print()

        pode_novo = saldo_devedor == 0 or limite > 0
        print("1. Novo Empréstimo" + ("" if pode_novo else " (indisponível)"))
        print("2. Quitar Empréstimo" + ("" if saldo_devedor > 0 else " (sem dívida ativa)"))
        print("3. Voltar")
        print()

        sub = input("Escolha uma opção: ").strip()

        if sub == '1':
            if limite <= 0:
                print("Você não possui limite disponível para novo empréstimo.")
                return
            try:
                valor = float(input("Digite o valor do empréstimo: "))
                meses = int(input("Digite o número de parcelas (meses): "))

                juros_prev = self.emprestimocase.calcular_juros(valor, meses)
                parcela_prev = self.emprestimocase.calcular_parcela(valor, meses)
                print()
                print("=== Simulação do Empréstimo ===")
                print(f"  Valor solicitado : R${valor:.2f}")
                print(f"  Taxa de juros    : 2% ao mês")
                print(f"  Juros total      : R${juros_prev:.2f}")
                print(f"  Total a pagar    : R${valor + juros_prev:.2f}")
                print(f"  Parcela mensal   : R${parcela_prev:.2f} x {meses}")
                print()

                confirmar = input("Confirmar empréstimo? (s/n): ").strip().lower()
                if confirmar == 's':
                    self.emprestimocase.executar(self.titular, valor, meses)
                    print(f"Empréstimo de R${valor:.2f} aprovado! {meses}x de R${parcela_prev:.2f}.")
                else:
                    print("Empréstimo cancelado.")
            except ValueError as e:
                print(f"Erro: {e}")

        elif sub == '2':
            if saldo_devedor == 0:
                print("Você não possui empréstimo ativo para quitar.")
                return
            try:
                print(f"Saldo devedor: R${saldo_devedor:.2f}")
                valor = float(input("Digite o valor a quitar: "))
                self.emprestimocase.quitar_emprestimo(self.titular, valor)
                print(f"Quitação de R${valor:.2f} realizada com sucesso.")
            except ValueError as e:
                print(f"Erro: {e}")

        elif sub == '3':
            return
        else:
            print("Opção inválida.")
