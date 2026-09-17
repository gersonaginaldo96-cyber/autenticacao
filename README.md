# Sistema de Login

Projeto simples em Python para cadastro e autenticação de usuários com SQLite.

## Funcionalidades
- Cadastro de usuários
- Login com validação de senha
- Redefinição de senha
- Testes automatizados com pytest

## Estrutura
- main.py: menu principal
- autenticacao/auth.py: lógica de autenticação
- models/database.py: conexão com o banco SQLite
- test_sistema.py: testes do sistema

## Como executar
1. Entre na pasta do projeto
2. Execute:

```bash
python main.py
```

## Como testar
```bash
python -m pytest -q
```


## Observações
- O arquivo de banco `usuarios.db` fica local e pode ser ignorado pelo Git.
- Arquivos temporários e caches também são ignorados pelo `.gitignore`.
