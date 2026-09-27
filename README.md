# Sistema de Login

Sistema de autenticação desenvolvido em Python para cadastro de usuários,
login e redefinição de senha. Os dados são armazenados localmente em um banco
SQLite. As senhas e respostas são protegidas com `bcrypt`, e as perguntas são
criptografadas com Fernet.

Este projeto tem finalidade de estudo e demonstra conceitos de organização de
módulos, persistência de dados, hash de senhas, validação de recuperação e
testes automatizados.

## Funcionalidades

- Cadastro de usuário com nome, senha, pergunta e resposta de validação.
- Normalização do nome de usuário com `strip()` e `casefold()`.
- Impedimento de nomes duplicados.
- Armazenamento da senha usando hash `bcrypt` com salt aleatório.
- Login com comparação segura por `bcrypt.checkpw()`.
- Verificação da existência de um usuário.
- Redefinição direta de senha para uso interno da aplicação.
- Redefinição de senha por pergunta e resposta de validação.
- Registro de tentativas incorretas de redefinição.
- Bloqueio após 3 tentativas incorretas durante 5 minutos.
- Verificação do bloqueio antes de exibir a pergunta de validação.
- Retorno ao menu após as operações; o programa só encerra pela opção 4.
- Criação automática das tabelas do banco na primeira conexão.
- Testes automatizados com `pytest`.

## Requisitos

- Python 3.10 ou superior.
- `bcrypt` para geração e verificação dos hashes.
- `cryptography` para criptografia Fernet das perguntas de validação.
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

Antes de executar o sistema, defina uma chave Fernet e mantenha-a fora do
código e do banco de dados. No PowerShell:

```powershell
$env:AUTH_ENCRYPTION_KEY = (python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
```

Use sempre a mesma chave nas execuções seguintes; sem ela, as perguntas
armazenadas não poderão ser descriptografadas.

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
3. Pergunta de validação.
4. Resposta de validação.

O nome é convertido para uma forma normalizada antes de ser salvo. A senha e a
resposta são transformadas em hashes `bcrypt`; os textos originais não são
armazenados. A pergunta é criptografada com Fernet porque precisa ser
recuperada para exibição.

### Login

Na opção 2, informe o nome e a senha. O sistema busca o hash salvo e usa
`bcrypt.checkpw()` para verificar a senha informada. O sistema não recupera nem
exibe a senha original.

### Redefinição de senha

Na opção 3, o sistema:

1. Recebe o nome do usuário.
2. Verifica se há um bloqueio ativo para esse nome.
3. Interrompe imediatamente o fluxo se o nome estiver bloqueado.
4. Busca e exibe a pergunta de validação.
5. Recebe a resposta.
6. Registra uma tentativa incorreta quando a resposta não confere.
7. Solicita a nova senha somente depois de uma resposta correta.
8. Limpa as tentativas após a validação bem-sucedida.

Após três respostas incorretas, o nome fica bloqueado por cinco minutos. Ao
escolher a opção 4, o programa encerra; as demais operações retornam ao menu.

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
- `autenticacao/validacao.py` gerencia a pergunta secreta, as tentativas e o bloqueio temporário.
- `models/database.py` garante a conexão SQLite e a criação das tabelas.

O fluxo padrão de cadastro e login funciona assim:

1. O usuário informa nome, senha, pergunta e resposta no menu.
2. O nome é normalizado com `strip()` e `casefold()` antes de ser salvo.
3. A senha e a resposta são armazenadas como hash `bcrypt`.
4. A pergunta de validação é criptografada com Fernet.
5. O login verifica a senha com `bcrypt.checkpw()` e não expõe o valor em texto puro.
6. A recuperação de senha exige a pergunta e a resposta corretas e pode bloquear o usuário por 5 minutos após 3 falhas.

### `main.py`

Contém o menu interativo e coordena as entradas do usuário. A regra de
aplicação é mantida nos módulos de autenticação e validação.

### `run.py`

É o ponto de entrada alternativo da aplicação. Ele importa e executa `main()`.

### `autenticacao/auth.py`

Contém as funções relacionadas à autenticação principal:

- `gerar_hash(senha)`: gera um hash `bcrypt`.
- `criar_usuario(nome, senha, pergunta, resposta)`: cria um usuário.
- `verificar_login(nome, senha)`: verifica as credenciais.
- `verificar_usuario(nome)`: verifica se o usuário existe.
- `gerar_senha_temp()`: gera uma senha numérica temporária de seis dígitos.
- `redefinir_senha(nome, nova_senha)`: troca a senha de um usuário existente.

### `autenticacao/validacao.py`

Concentra a lógica de pergunta de validação e controle de tentativas:

- `pergunta_de_validacao(...)`: confere pergunta e resposta.
- `resposta_da_pergunta_de_validacao(nome)`: retorna a pergunta cadastrada.
- `redefinicao_bloqueada(nome)`: verifica e atualiza o estado do bloqueio.
- `registrar_tentativa_incorreta(nome)`: registra uma falha.
- `limpar_tentativas(nome)`: remove o registro após sucesso.
- `validar_redefinicao(...)`: valida a recuperação sem alterar a senha.
- `redefinir_senha_com_validacao(...)`: valida e altera a senha.

### `models/database.py`

Contém `conectar_db()`, que abre `usuarios.db` e garante a existência das
tabelas `usuarios` e `redefinir_pin`.

### `test_sistema.py`

Contém testes de criação do banco, cadastro, login, hash, consulta da pergunta,
redefinição de senha e bloqueio após tentativas incorretas.

## Banco de dados

O arquivo `usuarios.db` é criado no diretório de trabalho em que a aplicação é
executada. A função `conectar_db()` cria automaticamente estas tabelas:

### Tabela `usuarios`

- `id`: identificador numérico.
- `nome`: nome normalizado e único.
- `senha`: hash `bcrypt` da senha.
- `pergunta_de_validacao`: pergunta cadastrada.
- `resposta_da_pergunta_de_validacao`: resposta usada na recuperação.
- `data_criacao`: data de criação automática.
- `ultima_alteracao`: campo de data mantido pelo schema atual.

### Tabela `redefinir_pin`

- `nome`: nome do usuário em recuperação.
- `tempo_hash`: campo reservado para evolução futura.
- `criado_em`: data de criação do registro.
- `tentativas`: número de tentativas incorretas.
- `bloqueado_ate`: data e hora até quando o bloqueio permanece ativo.

Não edite o arquivo `usuarios.db` manualmente durante a execução. Para começar
com uma base vazia em ambiente de desenvolvimento, encerre o programa e
remova o arquivo; ele será recriado na próxima execução.

## Como executar os testes

Para executar os testes funcionais atuais:

```bash
python -m pytest -q -k "not gerar_hash_e_deterministico"
```

O teste `test_gerar_hash_e_deterministico` existente espera que duas chamadas
de `gerar_hash('senha')` retornem exatamente o mesmo texto. Isso não é o
comportamento correto do `bcrypt`: cada chamada usa um salt novo, então os
hashes devem ser diferentes, enquanto `bcrypt.checkpw()` deve validar a senha.

Os demais testes devem passar normalmente. Para executar a suíte inteira e
visualizar esse teste específico:

```bash
python -m pytest -q
```

## Segurança atual

O projeto já usa `bcrypt` para as senhas e consultas SQL parametrizadas, mas
ainda deve ser considerado um projeto local ou educacional, não um sistema
pronto para produção.

Limitações conhecidas:

- As respostas de validação ainda são armazenadas em texto simples.
- O arquivo SQLite não é criptografado.
- O login não possui limite de tentativas.
- Não há política mínima de tamanho ou complexidade de senha.
- O fluxo pode revelar se um nome de usuário existe.
- A pergunta de validação não deve ser tratada como autenticação forte.
- O tratamento de exceções ainda exibe mensagens internas no cadastro.

Melhorias recomendadas:

1. Armazenar a resposta de validação com hash ou substituir o mecanismo por um
   token de recuperação.
2. Implementar limitação de tentativas também no login.
3. Criar regras mínimas para senhas.
4. Usar mensagens genéricas para reduzir a descoberta de usuários.
5. Proteger o arquivo do banco com permissões adequadas ou criptografia.
6. Registrar eventos de segurança sem expor detalhes internos ao usuário.

## Contribuição

Consulte [CONTRIBUTING.md](CONTRIBUTING.md) para o fluxo de branches, padrão
de commits e verificações recomendadas antes de enviar alterações.

## Licença

Este repositório não contém atualmente um arquivo de licença. Defina uma
licença antes de distribuir o projeto publicamente.
