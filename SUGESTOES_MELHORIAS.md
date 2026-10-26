# Sugestões de melhoria para o projecto de autenticação

Este documento resume as principais melhorias recomendadas para o projecto `autenticacao`, com foco em segurança, qualidade de código, usabilidade e manutenção.

## 1. Prioridade máxima: remover segredos hardcoded

### Problema
O código possui credenciais de e-mail e SMTP fixas no ficheiro de autenticação, o que representa um risco grave de segurança.

### Recomendação
- Remover valores como `seu_email`, `senha_email` e configurações SMTP do código.
- Guardar estas configurações em variáveis de ambiente.
- Criar um ficheiro `.env.example` com valores de exemplo.
- Usar bibliotecas como `python-dotenv` para carregar estas variáveis no ambiente local.

### Exemplo
```python
import os

EMAIL_FROM = os.getenv("EMAIL_FROM")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
``` 

## 2. Melhorar a gestão de segurança

### Problemas identificados
- O e-mail está a ser salvo como hash em vez de ser guardado em texto normal.
- O hash bcrypt é usado corretamente para senhas, mas a lógica global pode ser inconsistente.
- O SQLite não é encriptado; os dados ficam expostos no disco local.
- O projeto indica que não é adequado para produção.

### Recomendação
- Manter `password_hash` em hash bcrypt.
- Guardar `email` como campo normalizado, se for necessário para comunicação ou recuperação.
- Se for necessário ocultar dados sensíveis, usar uma estratégia clara e consistente.
- Para ambiente real, considerar encriptação de ficheiros, armazenamento seguro ou base de dados protegida.

## 3. Corrigir inconsistências na lógica de autenticação

### Problemas notáveis
- `criar_usuario()` valida o e-mail e depois guarda o e-mail hashed.
- A validação do e-mail depende de uma biblioteca externa que não está no `requirements.txt`.
- A validação de senha é pouco rigorosa e pode aceitar entradas inconsistentes.
- O sistema de login e de bloqueio pode revelar se um utilizador existe.

### Recomendação
- Centralizar toda a validação em uma função bem definida.
- Garantir que o mesmo critério seja usado em todas as decisões:
  - cadastro
  - login
  - redefinição de senha
- Definir regras claras para:
  - nome
  - e-mail
  - senha
  - tentativas máximas

## 4. Resolver o fluxo de recuperação de senha

### Problema
O README menciona que o código temporário é gerado, mas não é exibido ao utilizador no menu interativo.

### Recomendação
- Garantir que o código temporário seja mostrado no terminal para fins locais.
- Ou enviar o código por e-mail através de SMTP configurado corretamente.
- Definir regras de expiração e limite de tentativas.
- Garantir que o código seja armazenado como hash, não em texto puro.

## 5. Melhorar o modelo de dados

### Sugestão de estrutura
```text
usuarios
- id
- nome
- email
- senha_hash
- criado_em
- atualizado_em

redefinir_pin
- id
- usuario_id
- codigo_hash
- criado_em
- expira_em
- tentativas
- bloqueado_ate

login_bloqueios
- id
- usuario_id
- tentativas
- bloqueado_ate
```

### Recomendação
- Usar chaves estrangeiras quando apropriado.
- Normalizar o nome de utilizador e e-mail.
- Garantir que a base de dados seja criada de forma consistente.

## 6. Corrigir dependências e ambiente

### Problema
O ficheiro `requirements.txt` não contém todas as dependências necessárias.

### Recomendação
- Incluir todas as dependências usadas pelo projecto, incluindo:
  - bcrypt
  - pytest
  - prompt-toolkit
  - email-validator
- Criar um ambiente virtual separado para cada desenvolvimento.
- Documentar claramente o comando de instalação.

## 7. Melhorar testes automatizados

### Recomendação
Adicionar testes para:
- criação de utilizador com dados válidos
- rejeição de e-mail inválido
- rejeição de senha fraca
- login com conta bloqueada
- código temporário expirado
- múltiplas tentativas de redefinição
- caso de usuário inexistente

## 8. Melhorar a estrutura do projecto

### Sugestão de organização
```text
app/
  auth.py
  security.py
  validators.py
  config.py
models/
  database.py
core/
  settings.py
tests/
  test_auth.py
  test_reset.py
requirements.txt
.env.example
README.md
```

### Objetivo
Separar melhor:
- autenticação
- validação
- base de dados
- configuração
- testes

## 9. Melhorar a documentação

### Recomendações
- Explicar claramente o que é funcional e o que é apenas protótipo.
- Documentar as limitações conhecidas.
- Adicionar exemplos de uso em CLI.
- Explicar o fluxo de recuperação de senha e como testar manualmente.

## 10. Roadmap recomendado

### Fase 1: segurança
- remover credenciais hardcoded
- validar dados sensíveis
- separar configuração do código

### Fase 2: robustez
- corrigir regras de senha e e-mail
- melhorar gestão de bloqueios
- reforçar tratamento de erros

### Fase 3: usabilidade
- melhorar feedback no terminal
- mostrar código temporário corretamente
- melhorar mensagens ao utilizador

### Fase 4: manutenção
- reorganizar módulos
- aumentar cobertura de testes
- preparar a arquitetura para futuras evoluções

## Conclusão

O projecto tem uma boa base como exercício de estudo em Python, mas ainda precisa de melhorias antes de ser considerado uma solução segura ou adequada para uso real. As mudanças mais importantes são:

1. remover segredos fixos
2. corrigir validação e consistência
3. melhorar o fluxo de recuperação de senha
4. aumentar cobertura de testes
5. reforçar boas práticas de segurança

Este documento serve como guia para evoluir o projecto de forma mais segura e profissional.

## Observação final
O repositório deve continuar a ser tratado como projecto de aprendizagem e protótipo, não como solução final para autenticação em produção.
