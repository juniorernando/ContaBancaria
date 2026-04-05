# ContaBancaria

Sistema bancario em Python com persistencia SQLite, operacao via terminal e separacao por camadas (dominio, casos de uso, adaptadores e interface).

## Objetivo

Permitir operacoes bancarias com regras de negocio claras:

- Cadastro de novo usuario com criacao de conta.
- Login via terminal.
- Deposito.
- Saque com limite por horario.
- Consulta de saldo.
- Emprestimo com juros compostos.
- Quitacao de emprestimo.
- Historico de transacoes.

## Arquitetura

O projeto segue uma arquitetura em camadas:

- Dominio: entidades e contratos (interfaces).
- Use Cases: regras de negocio e orquestracao.
- Adapters/Repositories: implementacao de persistencia.
- Interface: interacao com usuario no terminal.
- Entry Point: composicao das dependencias e inicio do fluxo.

Arquivos principais:

- [lambda.py](lambda.py)
- [src/domain/entities/conta.py](src/domain/entities/conta.py)
- [src/domain/entities/transaction.py](src/domain/entities/transaction.py)
- [src/domain/repositories/conta_repository.py](src/domain/repositories/conta_repository.py)
- [src/use_cases/criar_conta_usuario.py](src/use_cases/criar_conta_usuario.py)
- [src/use_cases/depositar.py](src/use_cases/depositar.py)
- [src/use_cases/sacar.py](src/use_cases/sacar.py)
- [src/use_cases/ver_saldo.py](src/use_cases/ver_saldo.py)
- [src/use_cases/listar_historico.py](src/use_cases/listar_historico.py)
- [src/use_cases/emprestimo.py](src/use_cases/emprestimo.py)
- [src/adapters/repositories/sqlite_conta_repository.py](src/adapters/repositories/sqlite_conta_repository.py)
- [src/adapters/repositories/memoria_conta_repository.py](src/adapters/repositories/memoria_conta_repository.py)
- [src/interface/inicio.py](src/interface/inicio.py)
- [src/interface/login.py](src/interface/login.py)
- [src/interface/menu.py](src/interface/menu.py)

## Estrutura do Projeto

```text
ContaBancaria/
|- lambda.py
|- data/
|- src/
|  |- adapters/repositories/
|  |- domain/entities/
|  |- domain/repositories/
|  |- interface/
|  |- use_cases/
|- tests/
```

## Fluxo de Execucao

1. O sistema inicia em [lambda.py](lambda.py).
2. O repositorio SQLite e criado.
3. Opcionalmente, um cadastro inicial pode ocorrer por variaveis de ambiente.
4. A interface inicial apresenta:
- Usuario existente
- Novo usuario
5. O login e validado.
6. O menu de operacoes bancarias e exibido.

## Regras de Negocio

### Cadastro de Usuario e Conta

- Nome, email e senha sao obrigatorios.
- Email e normalizado para minusculo.
- Saldo inicial nao pode ser negativo.
- Email deve ser unico no banco.
- Titular da conta deve ser unico.
- Criacao de usuario e conta ocorre em uma unica transacao.

Referencias:

- [src/use_cases/criar_conta_usuario.py](src/use_cases/criar_conta_usuario.py)
- [src/adapters/repositories/sqlite_conta_repository.py](src/adapters/repositories/sqlite_conta_repository.py)

### Login

- Senha minima de 6 caracteres.
- Senha "123456" e bloqueada.
- Maximo de 3 tentativas.
- Entrada de senha mascarada no terminal.

Referencia:

- [src/interface/login.py](src/interface/login.py)

### Deposito

- Valor deve ser maior que 0.
- Saldo da conta e atualizado.
- Transacao e registrada no historico.

Referencia:

- [src/use_cases/depositar.py](src/use_cases/depositar.py)

### Saque

- Valor deve ser maior que 0.
- Limite depende do horario:
- Noturno (22h ate 6h): usa `LIMITE_NOTURNO`.
- Diurno (6h ate 22h): usa `LIMITE_DIURNO`.
- Nao permite sacar acima do saldo.
- Registra transacao de saque.

Referencia:

- [src/use_cases/sacar.py](src/use_cases/sacar.py)

### Emprestimo

- Valor deve ser maior que 0.
- Meses deve ser maior que 0.
- Limite do emprestimo: 80% do saldo atual.
- Taxa de juros: 2% ao mes (juros compostos).
- Ao contratar:
- Credita valor solicitado no saldo.
- Soma total com juros em `saldo_emprestimo`.
- Registra transacao de emprestimo.
- Quitacao:
- So permite se houver divida ativa.
- Valor de quitacao deve ser positivo.
- Nao pode exceder saldo da conta.
- Nao pode exceder saldo devedor.

Referencia:

- [src/use_cases/emprestimo.py](src/use_cases/emprestimo.py)

### Historico

- Lista transacoes do titular da mais recente para a mais antiga.

Referencia:

- [src/use_cases/listar_historico.py](src/use_cases/listar_historico.py)

## Funcoes e Responsabilidades

### Entry Point

- [lambda.py](lambda.py)
- `_cadastrar_nova_conta_se_configurada`: tenta criar conta pelo conjunto de variaveis BANCO_NOVO_*.
- Bloco principal: inicializa repositorio, interface inicial, login e menu.

### Interface

- [src/interface/inicio.py](src/interface/inicio.py)
- `escolher_fluxo_inicial`: menu inicial (usuario existente, novo usuario, sair).
- `_fluxo_usuario_existente`: coleta credenciais para login.
- `_fluxo_novo_usuario`: coleta dados, valida senha e cria usuario/conta.

- [src/interface/login.py](src/interface/login.py)
- `_input_senha`: leitura de senha com mascaramento.
- `sistemaLogin`: valida senha e controla tentativas.

- [src/interface/menu.py](src/interface/menu.py)
- `exibir`: exibe menu principal.
- `escolher_opcao`: executa operacoes bancarias.
- `_menu_emprestimo`: submenu de contratacao e quitacao.

### Use Cases

- [src/use_cases/criar_conta_usuario.py](src/use_cases/criar_conta_usuario.py)
- `executar`: valida entradas e delega persistencia ao repositorio.

- [src/use_cases/depositar.py](src/use_cases/depositar.py)
- `executar`: valida valor, atualiza saldo e registra transacao.

- [src/use_cases/sacar.py](src/use_cases/sacar.py)
- `_limite_atual`: define limite de saque por faixa de horario.
- `executar`: valida valor, limite e saldo; registra transacao.

- [src/use_cases/ver_saldo.py](src/use_cases/ver_saldo.py)
- `executar`: retorna saldo da conta.

- [src/use_cases/listar_historico.py](src/use_cases/listar_historico.py)
- `executar`: retorna historico de transacoes do titular.

- [src/use_cases/emprestimo.py](src/use_cases/emprestimo.py)
- `executar`: valida e contrata emprestimo.
- `calcular_juros`: juros compostos de 2% ao mes.
- `calcular_parcela`: parcela mensal.
- `saldo_emprestimo`: consulta saldo devedor.
- `quitar_emprestimo`: baixa divida com validacoes.

### Repositorios

- [src/domain/repositories/conta_repository.py](src/domain/repositories/conta_repository.py)
- Contrato para criacao de conta, busca, salvamento e historico.

- [src/adapters/repositories/sqlite_conta_repository.py](src/adapters/repositories/sqlite_conta_repository.py)
- `_init_db`: cria tabelas `usuarios`, `contas`, `transacoes`.
- `_migrar_tabela_contas`: adiciona colunas ausentes em bancos antigos.
- `criar_conta_usuario`: cria usuario + conta com tratamento de duplicidade.
- `buscar`: busca conta por titular (e cria com saldo 0 quando inexistente).
- `salvar`: atualiza saldo e saldo de emprestimo.
- `registrar_transacao`: persiste movimentacoes.
- `listar_transacoes`: retorna historico ordenado.

- [src/adapters/repositories/memoria_conta_repository.py](src/adapters/repositories/memoria_conta_repository.py)
- Implementacao em memoria para cenarios de teste e desenvolvimento.

## Modelo de Dados SQLite

Tabela `usuarios`:

- `id` (PK)
- `nome`
- `email` (UNIQUE)
- `senha_hash`

Tabela `contas`:

- `titular` (PK)
- `saldo`
- `saldo_emprestimo`
- `usuario_id` (UNIQUE, FK para `usuarios.id`)

Tabela `transacoes`:

- `id` (PK)
- `titular`
- `tipo`
- `valor`
- `data_hora`
- `descricao`

Referencia:

- [src/adapters/repositories/sqlite_conta_repository.py](src/adapters/repositories/sqlite_conta_repository.py)

## Variaveis de Ambiente

Exemplo de [ .env ](.env) sem espacos em volta do `=`:

```env
BANCO_USUARIO=rafa
BANCO_SENHA=senha123
LIMITE_DIURNO=5000.0
LIMITE_NOTURNO=500.0

# Opcional: cadastro automatico no boot
BANCO_NOVO_NOME=
BANCO_NOVO_EMAIL=
BANCO_NOVA_SENHA=
BANCO_NOVO_SALDO=0
```

## Como Executar

1. Ative o ambiente virtual.
2. Instale as dependencias.
3. Execute o sistema:

```powershell
python lambda.py
```

## Testes

Executar todos os testes:

```powershell
python -m pytest -q
```

Arquivos de teste atuais:

- [tests/test_emprestimo.py](tests/test_emprestimo.py)
- [tests/test_criar_conta_usuario.py](tests/test_criar_conta_usuario.py)
- [tests/test_bootstrap_cadastro.py](tests/test_bootstrap_cadastro.py)

## Melhorias Futuras

- Autenticacao real consultando usuario/senha no banco.
- Armazenar senha com hash forte (exemplo: bcrypt).
- Aumentar cobertura de testes para saque, deposito e login.
- Padronizar nomenclatura de classe `emprestimo` para `EmprestimoUseCase`.
