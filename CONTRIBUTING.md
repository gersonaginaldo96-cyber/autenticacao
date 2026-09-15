# Guia de contribuição e commits

## 1. Fluxo recomendado

1. Crie uma branch para a feature ou correção.
2. Faça alterações pequenas e focadas.
3. Teste antes de confirmar.
4. Faça commit com mensagem clara.
5. Envie a branch para o repositório remoto.

Exemplo:

```bash
git checkout -b feat/cadastro-usuario
git add .
git commit -m "feat: adiciona cadastro de usuários"
git push origin feat/cadastro-usuario
```

## 2. Padrão de mensagens de commit

Use o formato:

```bash
tipo: descrição curta
```

Tipos comuns:
- feat: nova funcionalidade
- fix: correção de bug
- docs: documentação
- test: testes
- refactor: reorganização do código
- chore: tarefas de manutenção

Exemplos:
- `feat: adiciona login do usuário`
- `fix: corrige erro na redefinição de senha`
- `test: adiciona testes de autenticação`
- `docs: adiciona README e guia de contribuição`

## 3. Boas práticas

- um commit deve ter uma finalidade clara
- evite misturar várias mudanças em um único commit
- escreva mensagens em português ou inglês, mas mantenha consistência
- prefira descrições curtas, objetivas e específicas

## 4. Antes de confirmar

Execute testes e validações:

```bash
python -m pytest -q
```

## 5. Estrutura de branches

Exemplos:
- `main`: versão estável
- `develop`: desenvolvimento
- `feat/nome-da-feature`
- `fix/nome-do-bug`

## 6. Recomendação final

Para este projeto, o fluxo ideal é:

```bash
git checkout -b feat/sistema-autenticacao
git add .
git commit -m "feat: implementa autenticação de usuários"
```

Isso ajuda a manter o histórico do Git organizado e facilita a revisão de mudanças.
