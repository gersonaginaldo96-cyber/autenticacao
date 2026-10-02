# Sistema de Login

Sistema de autenticação desenvolvido em Python para cadastro de usuários,
login e redefinição de senha. Os dados são armazenados localmente em um banco
SQLite. As senhas e os códigos temporários de recuperação são protegidos com
hashes `bcrypt`.

Este projeto tem finalidade de estudo e demonstra conceitos de organização de
módulos, persistência de dados, hash de senhas, validação de recuperação e
testes automatizados.

## Funcionalidades

- Cadastro de usuário com nome e senha.
- Normalização do nome de usuário com `strip()` e `casefold()`.
- Impedimento de nomes duplicados.
- Armazenamento da senha usando hash `bcrypt` com salt aleatório.
- Login com comparação segura por `bcrypt.checkpw()`.
- Verificação da existência de um usuário.
- Redefinição direta de senha para uso interno da aplicação.
- Redefinição de senha por código temporário de seis dígitos.
- Expiração do código após 10 minutos e uso único após a redefinição.
- Registro de tentativas incorretas de redefinição.
- Bloqueio após 3 tentativas incorretas durante 10 minutos.
- Verificação do bloqueio antes de gerar um código temporário.
- Retorno ao menu após as operações; o programa só encerra pela opção 4.
- Criação automática das tabelas do banco na primeira conexão.
- Testes automatizados com `pytest`.

## Requisitos

- Python 3.10 ou superior.
- `bcrypt` para geração e verificação dos hashes.
- `pytest` para executar os testes.

O projeto usa apenas SQLite da biblioteca padrão, portanto não é necessário
instalar ou configurar um servidor de banco de dados.

## Instalação

Abra um terminal na pasta do projeto e, opcionalmente, crie um ambiente virtual:

```bash
python -m venv .venv
```

No Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

No Linux ou macOS:

```bash
source .venv/bin/activate
```

Instale as dependências:

```bash
python -m pip install -r requirements.txt
```

## Como executar

Na raiz do projeto, execute:

```bash
python run.py
```

Também é possível executar diretamente:

```bash
python main.py
```

O menu apresenta quatro opções:

```text
1 - Cadastrar usuário
2 - Fazer login
3 - Redefinir senha
4 - Sair
```

### Cadastro

Na opção 1, informe:

1. Nome do usuário.
2. Senha.

O nome é convertido para uma forma normalizada antes de ser salvo. A senha é
armazenada como hash `bcrypt`, não como texto original.

### Login

Na opção 2, informe o nome e a senha. O sistema busca o hash salvo e usa
`bcrypt.checkpw()` para verificar a senha informada. O sistema não recupera nem
exibe a senha original.

### Redefinição de senha

Na opção 3, o sistema:

1. Recebe o nome do usuário.
2. Verifica se há um bloqueio ativo para esse nome.
3. Gera um código temporário e o exibe no console.
4. Solicita o código e a nova senha.
5. Compara o código informado com o hash armazenado.
6. Remove o código após redefinir a senha com sucesso.

O código expira após 10 minutos. Após três códigos incorretos, o nome fica
bloqueado por cinco minutos. Como o código é exibido no próprio console, este
fluxo serve para demonstração local; um sistema real deve enviá-lo por um canal
separado e verificado. Ao escolher a opção 4, o programa encerra; as demais
operações retornam ao menu.

## Estrutura do projeto

```text
.
├── main.py
├── run.py
├── README.md
├── CONTRIBUTING.md
├── roadmap.rd
├── test_sistema.py
├── autenticacao/
│   ├── __init__.py
│   ├── auth.py
│   └── validacao.py
└── models/
	├── __init__.py
	└── database.py
```

### Fluxo de execução e regras de negócio

O sistema é organizado em camadas simples:

- `main.py` coordena o menu de console e a interação com o usuário.
- `autenticacao/auth.py` cuida da criação, validação e alteração de credenciais.
- `autenticacao/validacao.py` gerencia o código temporário, as tentativas e o bloqueio.
- `models/database.py` garante a conexão SQLite e a criação das tabelas.

O fluxo padrão de cadastro e login funciona assim:

1. O usuário informa nome e senha no menu.
2. O nome é normalizado com `strip()` e `casefold()` antes de ser salvo.
3. A senha é armazenada como hash `bcrypt`.
4. O login verifica a senha com `bcrypt.checkpw()` e não expõe o valor em texto puro.
5. A recuperação gera um PIN de seis dígitos, armazena somente seu hash e bloqueia o usuário por 5 minutos após 3 falhas.

### `main.py`

Contém o menu interativo e coordena as entradas do usuário. A regra de
aplicação é mantida nos módulos de autenticação e validação.

### `run.py`

É o ponto de entrada alternativo da aplicação. Ele importa e executa `main()`.

### `autenticacao/auth.py`

Contém as funções relacionadas à autenticação principal:

- `gerar_hash(senha)`: gera um hash `bcrypt`.
- `criar_usuario(nome, senha)`: cria um usuário.
- `verificar_login(nome, senha)`: verifica as credenciais.
- `verificar_usuario(nome)`: verifica se o usuário existe.
- `gerar_senha_temp()`: gera uma senha numérica temporária de seis dígitos.
- `redefinir_senha(nome, nova_senha)`: troca a senha de um usuário existente.

### `autenticacao/validacao.py`

Concentra a lógica de recuperação por código e controle de tentativas:

- `solicitar_codigo_temporario(nome)`: gera o código e salva seu hash.
- `redefinir_senha_com_codigo(...)`: verifica validade e código antes da troca.
- `redefinicao_bloqueada(nome)`: verifica e atualiza o estado do bloqueio.
- `registrar_tentativa_incorreta(nome)`: registra uma falha.
- `limpar_tentativas(nome)`: remove o código e o registro de tentativas.

### `models/database.py`

Contém `conectar_db()`, que abre `usuarios.db` e garante a existência das
tabelas `usuarios` e `redefinir_pin`.

### `test_sistema.py`

Contém testes de criação do banco, cadastro, login, hash, recuperação por PIN,
expiração do código e bloqueio após tentativas incorretas.

## Banco de dados

O arquivo `usuarios.db` é criado no diretório de trabalho em que a aplicação é
executada. A função `conectar_db()` cria automaticamente estas tabelas:

### Tabela `usuarios`

- `id`: identificador numérico.
- `nome`: nome normalizado e único.
- `senha`: hash `bcrypt` da senha.
- `data_criacao`: data de criação automática.
- `ultima_alteracao`: campo de data mantido pelo schema atual.

### Tabela `redefinir_pin`

- `nome`: nome do usuário em recuperação.
- `tempo_hash`: hash `bcrypt` do código temporário.
- `criado_em`: data de criação do registro.
- `tentativas`: número de tentativas incorretas.
- `bloqueado_ate`: data e hora até quando o bloqueio permanece ativo.

Não edite o arquivo `usuarios.db` manualmente durante a execução. Para começar
com uma base vazia em ambiente de desenvolvimento, encerre o programa e
remova o arquivo; ele será recriado na próxima execução.

Atualmente, esse arquivo **não é criptografado**. O hash `bcrypt` protege o
valor original das senhas, mas não criptografa o banco inteiro nem os demais
dados armazenados nele.

## Como executar os testes

Para executar os testes:

```bash
python -m pytest -q
```

## Segurança atual

O projeto já usa `bcrypt` para as senhas e consultas SQL parametrizadas, mas
ainda deve ser considerado um projeto local ou educacional, não um sistema
pronto para produção.

Limitações conhecidas:

- O arquivo SQLite é armazenado sem criptografia; quem obtiver acesso ao arquivo
  poderá ler os dados, embora as senhas estejam armazenadas como hashes.
- O login não possui limite de tentativas.
- O fluxo pode revelar se um nome de usuário existe.
- O código de recuperação é exibido no console e não é enviado por um canal independente.
- O tratamento de exceções ainda exibe mensagens internas no cadastro.

### Proteção do arquivo do banco

A criptografia do banco **ainda não está implementada**. Para uso local no
Windows, uma primeira medida é ativar o BitLocker ou a Criptografia do
dispositivo, quando disponíveis, e manter backups protegidos. Isso ajuda a
proteger os arquivos quando o dispositivo está bloqueado ou é perdido, mas não
protege o banco enquanto a aplicação está aberta e o usuário já está conectado.

Se for necessário criptografar o próprio arquivo `usuarios.db`, uma opção é
migrar para uma distribuição do SQLite com SQLCipher. Isso exige trocar o
módulo usado para abrir o banco e configurar uma chave antes de qualquer
consulta. O `sqlite3` padrão usado atualmente não abre um banco criptografado
por SQLCipher.

Antes de uma migração:

1. Feche a aplicação e faça uma cópia de segurança do banco atual.
2. Exporte os dados para um novo banco criptografado usando o procedimento
	suportado pela versão do SQLCipher escolhida. Não basta configurar uma chave
	ao abrir o arquivo atual, que está em texto claro.
3. Guarde a chave fora do código-fonte e do banco, em um armazenamento seguro
	apropriado ao sistema operacional. Inclua um plano seguro para disponibilizar
	a chave aos backups.
4. Teste o login, a recuperação de senha e a leitura dos registros no novo
	banco antes de substituir o arquivo original.

Sem a chave, os dados criptografados não podem ser recuperados. A criptografia
do banco reduz o risco de exposição de uma cópia do arquivo, mas não substitui
o controle de acesso ao computador, a proteção da chave nem backups seguros.

### Melhorias sugeridas

1. Enviar o código de recuperação por um canal independente e verificado.
2. Implementar limitação de tentativas também no login.
3. Usar mensagens genéricas para reduzir a descoberta de usuários.
4. Ativar a criptografia do dispositivo e proteger os backups; avaliar SQLCipher
   se for necessária criptografia específica do arquivo do banco.
5. Proteger a chave de criptografia fora do repositório e do banco, caso SQLCipher
   seja adotado.
6. Registrar eventos de segurança sem expor detalhes internos ao usuário.

## Contribuição

Consulte [CONTRIBUTING.md](CONTRIBUTING.md) para o fluxo de branches, padrão
de commits e verificações recomendadas antes de enviar alterações.

## Licença

Este repositório não contém atualmente um arquivo de licença. Defina uma
licença antes de distribuir o projeto publicamente.
