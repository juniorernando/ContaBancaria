import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest
from unittest.mock import MagicMock
from domain.entities.conta import Conta
from domain.entities.transaction import Transaction
from use_cases.emprestimo import emprestimo


def make_repo(saldo: float = 1000.0, saldo_emprestimo: float = 0.0):
    """Cria um repositório mock com uma conta pré-configurada."""
    repo = MagicMock()
    conta = Conta(titular="joao", saldo=saldo, saldo_emprestimo=saldo_emprestimo)
    repo.buscar.return_value = conta
    return repo, conta


# ── calcular_juros ──────────────────────────────────────────────────────────

class TestCalcularJuros:
    def test_juros_positivo(self):
        uc = emprestimo(MagicMock())
        juros = uc.calcular_juros(1000.0, 12)
        assert juros > 0

    def test_juros_formula_correta(self):
        uc = emprestimo(MagicMock())
        juros = uc.calcular_juros(1000.0, 1)
        assert round(juros, 2) == round(1000 * 1.02 - 1000, 2)


# ── calcular_parcela ────────────────────────────────────────────────────────

class TestCalcularParcela:
    def test_parcela_positiva(self):
        uc = emprestimo(MagicMock())
        parcela = uc.calcular_parcela(1000.0, 10)
        assert parcela > 0

    def test_parcela_e_total_dividido_por_meses(self):
        uc = emprestimo(MagicMock())
        juros = uc.calcular_juros(1000.0, 10)
        total = 1000.0 + juros
        assert round(uc.calcular_parcela(1000.0, 10), 6) == round(total / 10, 6)


# ── executar ────────────────────────────────────────────────────────────────

class TestExecutar:
    def test_emprestimo_aprovado_aumenta_saldo(self):
        repo, conta = make_repo(saldo=1000.0)
        uc = emprestimo(repo)
        uc.executar("joao", 500.0, 12)
        assert conta.saldo == 1500.0

    def test_emprestimo_registra_saldo_devedor(self):
        repo, conta = make_repo(saldo=1000.0)
        uc = emprestimo(repo)
        resultado = uc.executar("joao", 500.0, 12)
        assert conta.saldo_emprestimo == resultado["total"]

    def test_retorna_dict_com_campos_esperados(self):
        repo, _ = make_repo(saldo=1000.0)
        uc = emprestimo(repo)
        resultado = uc.executar("joao", 500.0, 12)
        assert set(resultado.keys()) == {"valor", "meses", "juros", "total", "parcela"}

    def test_salva_e_registra_transacao(self):
        repo, _ = make_repo(saldo=1000.0)
        uc = emprestimo(repo)
        uc.executar("joao", 500.0, 12)
        repo.salvar.assert_called_once()
        repo.registrar_transacao.assert_called_once()

    def test_valor_negativo_levanta_erro(self):
        repo, _ = make_repo()
        uc = emprestimo(repo)
        with pytest.raises(ValueError, match="positivo"):
            uc.executar("joao", -100.0, 12)

    def test_valor_zero_levanta_erro(self):
        repo, _ = make_repo()
        uc = emprestimo(repo)
        with pytest.raises(ValueError):
            uc.executar("joao", 0.0, 12)

    def test_meses_zero_levanta_erro(self):
        repo, _ = make_repo()
        uc = emprestimo(repo)
        with pytest.raises(ValueError, match="meses"):
            uc.executar("joao", 100.0, 0)

    def test_excede_limite_80_levanta_erro(self):
        repo, _ = make_repo(saldo=1000.0)
        uc = emprestimo(repo)
        with pytest.raises(ValueError, match="80%"):
            uc.executar("joao", 900.0, 12)  # limite = 800

    def test_exatamente_no_limite_80_aprovado(self):
        repo, conta = make_repo(saldo=1000.0)
        uc = emprestimo(repo)
        uc.executar("joao", 800.0, 12)
        assert conta.saldo == 1800.0


# ── saldo_emprestimo ────────────────────────────────────────────────────────

class TestSaldoEmprestimo:
    def test_retorna_saldo_devedor(self):
        repo, _ = make_repo(saldo=1000.0, saldo_emprestimo=350.0)
        uc = emprestimo(repo)
        assert uc.saldo_emprestimo("joao") == 350.0

    def test_retorna_zero_sem_emprestimo(self):
        repo, _ = make_repo(saldo=1000.0, saldo_emprestimo=0.0)
        uc = emprestimo(repo)
        assert uc.saldo_emprestimo("joao") == 0.0


# ── quitar_emprestimo ───────────────────────────────────────────────────────

class TestQuitarEmprestimo:
    def test_quitar_reduz_saldo_e_divida(self):
        repo, conta = make_repo(saldo=1500.0, saldo_emprestimo=500.0)
        uc = emprestimo(repo)
        uc.quitar_emprestimo("joao", 200.0)
        assert conta.saldo == 1300.0
        assert conta.saldo_emprestimo == 300.0

    def test_quitar_total_zera_divida(self):
        repo, conta = make_repo(saldo=1500.0, saldo_emprestimo=500.0)
        uc = emprestimo(repo)
        uc.quitar_emprestimo("joao", 500.0)
        assert conta.saldo_emprestimo == 0.0

    def test_salva_e_registra_transacao(self):
        repo, _ = make_repo(saldo=1500.0, saldo_emprestimo=500.0)
        uc = emprestimo(repo)
        uc.quitar_emprestimo("joao", 100.0)
        repo.salvar.assert_called_once()
        repo.registrar_transacao.assert_called_once()

    def test_valor_negativo_levanta_erro(self):
        repo, _ = make_repo(saldo=1500.0, saldo_emprestimo=500.0)
        uc = emprestimo(repo)
        with pytest.raises(ValueError, match="positivo"):
            uc.quitar_emprestimo("joao", -50.0)

    def test_valor_zero_levanta_erro(self):
        repo, _ = make_repo(saldo=1500.0, saldo_emprestimo=500.0)
        uc = emprestimo(repo)
        with pytest.raises(ValueError):
            uc.quitar_emprestimo("joao", 0.0)

    def test_sem_emprestimo_ativo_levanta_erro(self):
        repo, _ = make_repo(saldo=1000.0, saldo_emprestimo=0.0)
        uc = emprestimo(repo)
        with pytest.raises(ValueError, match="empréstimo ativo"):
            uc.quitar_emprestimo("joao", 100.0)

    def test_saldo_insuficiente_levanta_erro(self):
        repo, _ = make_repo(saldo=50.0, saldo_emprestimo=500.0)
        uc = emprestimo(repo)
        with pytest.raises(ValueError, match="insuficiente"):
            uc.quitar_emprestimo("joao", 200.0)

    def test_excede_saldo_devedor_levanta_erro(self):
        repo, _ = make_repo(saldo=2000.0, saldo_emprestimo=300.0)
        uc = emprestimo(repo)
        with pytest.raises(ValueError, match="saldo devedor"):
            uc.quitar_emprestimo("joao", 400.0)
