from autenticacao.auth import (
    criar_usuario,
    verificar_login,
    redefinir_senha,
)
from autenticacao.validacao import (
    resposta_da_pergunta_de_validacao,
    redefinicao_bloqueada,
    validar_redefinicao,
)


def main() -> None:
    """Executa o loop principal do menu de interação com o usuário."""
    print('=== Sistema de Login ===')

    while True:
        print('\n1 - Cadastrar usuário')
        print('2 - Fazer login')
        print('3 - redefinir senha')
        print('4 - Sair')
        opcao = input('Escolha uma opção: ').strip()

        if opcao == '1':
            nome = input('Digite o nome: ')
            senha = input('Digite a senha: ')
            pergunta = input('Digite uma pergunta de validação: ')
            resposta = input('Digite a resposta de validação: ')
            criar_usuario(nome, senha, pergunta, resposta)

        elif opcao == '2':
            nome = input('Digite o nome: ')
            senha = input('Digite a senha: ')

            if verificar_login(nome, senha):
                print(f'Login realizado com sucesso! Bem-vindo(a), {nome.strip().casefold()}')
            else:
                print('Nome ou senha incorretos.')

        elif opcao == '3':
            nome = input("digita o seu nome: ")
            nome_normalizado = nome.strip().casefold()

            if redefinicao_bloqueada(nome_normalizado):
                print('Nome bloqueado devido a excessivas tentativas.')
                continue

            pergunta = resposta_da_pergunta_de_validacao(nome)

            if pergunta is None:
                print("nao foi possivel redefinir")
                continue
            print(f"pergunta de validacao : {pergunta}")
            resposta = input('Resposta: ')

            if not validar_redefinicao(nome, pergunta, resposta):
                continue

            nova_senha = input("Digita a nova senha: ")

            if redefinir_senha(nome, nova_senha):
                print('senha redefinida com sucesso')

        elif opcao == '4':
            print("saindo do sistema")
            break


if __name__ == '__main__':
    main()



