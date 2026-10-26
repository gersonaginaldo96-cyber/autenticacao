# Sistema de autenticação

Aplicação de linha de comando em Python para cadastrar usuários, validar
credenciais e redefinir senhas. Os dados são armazenados em um banco SQLite
local; senhas e códigos temporários são protegidos com hashes `bcrypt`.

O projeto é voltado a estudo e desenvolvimento local. Não deve ser considerado
pronto para uso em produção.

## Funcionalidades

- Cadastro com nome, senha e endereço de e-mail.
- Normalização de nomes e e-mails com `strip()` e `casefold()`.
- Validação de senha: pelo menos 8 caracteres e um caractere especial aceito
  pelo código (`@`, `#`, `$`, `%`, `^`, `&`, `*`, `!`, `>`, `<`, `:`, `.`,
  `º`, `ç`, `'` ou `«`).
- Armazenamento de senhas com `bcrypt` e comparação com `bcrypt.checkpw()`.
- Máscara com `prompt_toolkit` para as senhas digitadas no cadastro, no login e
  na redefinição.
- Bloqueio temporário de login após 3 senhas incorretas para uma conta existente
  (10 minutos).
- Geração de código temporário de 6 dígitos para recuperação, com validade de
  10 minutos e armazenamento do hash.
- Bloqueio da recuperação por 5 minutos após 3 códigos incorretos.
- Criação automática das tabelas SQLite na primeira conexão.

## Requisitos

- Python 3.10 ou superior.
- Dependências listadas em `requirements.txt` (`bcrypt` e `pytest`).
- `prompt-toolkit`, usado para mascarar as senhas durante a digitação, não está
  listado em `requirements.txt`.
- A validação de e-mail também importa `email-validator`, que não está listado
  em `requirements.txt`. Para habilitar o cadastro, instale-o separadamente:

```bash
python -m pip install email-validator
```

A validação de e-mail verifica a entregabilidade e pode precisar de acesso à
internet. O banco de dados usa SQLite da biblioteca padrão; não é necessário
instalar um servidor de banco de dados.

## Instalação

Na pasta do projeto, crie e ative um ambiente virtual (recomendado).

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Linux ou macOS:

```bash
python -m venv .venv
source .venv/bin/activate
```

Instale as dependências e os pacotes adicionais:

```bash
python -m pip install -r requirements.txt
python -m pip install prompt-toolkit email-validator
```

## Execução

Na raiz do projeto, inicie a aplicação com:

```bash
python run.py
```

Como alternativa, execute `python main.py`. O menu oferece:

```text
1 - Cadastrar usuário
2 - Fazer login
3 - Redefinir senha
4 - Sair
```

No cadastro, informe nome, senha e e-mail. As senhas digitadas no cadastro, no
login e na redefinição são solicitadas com `prompt_toolkit` e aparecem
mascaradas no terminal. Na recuperação pelo menu, o programa gera um código e
pede o código e a nova senha, mas atualmente não mostra nem envia o código.
Embora exista uma função auxiliar de envio de e-mail no módulo de autenticação,
ela não é usada pelo fluxo atual de recuperação.

## Estrutura do projeto

```text
.
├── autenticacao/
│   ├── __init__.py
│   ├── auth.py
│   └── validacao.py
├── models/
│   ├── __init__.py
│   └── database.py
├── main.py
├── run.py
├── requirements.txt
├── test_sistema.py
├── README.md
└── CONTRIBUTING.md
```

- `main.py`: menu interativo e coordenação das entradas do usuário.
- `prompt-toolkit`: máscara de entrada de senhas no cadastro, login e
  redefinição.
- `run.py`: ponto de entrada alternativo que chama `main()`.
- `autenticacao/auth.py`: cadastro, validação de senha, login, hashes e
  bloqueios de login.
- `autenticacao/validacao.py`: solicitação e validação dos códigos de
  recuperação, expiração e bloqueio por tentativas.
- `models/database.py`: conexão SQLite e criação/atualização das tabelas.
- `test_sistema.py`: testes automatizados com `pytest`.

## Banco de dados

O arquivo `usuarios.db` é criado no diretório de trabalho atual quando a
aplicação se conecta ao banco. As tabelas são:

- `usuarios`: identificador, nome, hash da senha, valor de e-mail, data de
  criação e data de alteração.
- `redefinir_pin`: hash do código temporário, horário de criação, tentativas e
  prazo de bloqueio da recuperação.
- `login_bloqueios`: tentativas de login e prazo de bloqueio por nome.

O SQLite padrão não criptografa o arquivo do banco. Os hashes protegem as
senhas e os códigos temporários, mas não criptografam o banco inteiro nem os
demais campos. O arquivo local é ignorado pelo Git.

## Testes

Execute os testes com:

```bash
python -m pytest -q
```

Os testes usam bancos temporários para evitar alterar o `usuarios.db` local.

## Limitações conhecidas

- O menu não mostra nem envia o código de recuperação que gera; assim, não é
  possível concluir a recuperação pelo fluxo interativo atual. O módulo aceita
  o código por sua função de redefinição, mas a interface não o disponibiliza.
- O módulo tem um auxiliar de envio SMTP, mas o fluxo de recuperação não o
  chama. Não use credenciais SMTP embutidas no código; mantenha credenciais
  fora do repositório e configure-as por um mecanismo seguro antes de integrar
  esse envio.
- A validação de e-mail depende do pacote `email-validator`, ausente da lista
  atual de dependências, e de conectividade para verificar entregabilidade.
- O bloqueio de login registra falhas para nomes de usuários existentes, o que
  pode permitir inferir se uma conta existe.
- A função interna `redefinir_senha()` não aplica a mesma validação de senha
  usada no cadastro e na recuperação por código.
- O arquivo SQLite é armazenado sem criptografia. Proteja o dispositivo e os
  backups; a criptografia do dispositivo não protege o arquivo enquanto a
  sessão está desbloqueada.

Consulte [CONTRIBUTING.md](CONTRIBUTING.md) para orientações de contribuição.
O repositório não contém um arquivo de licença.
