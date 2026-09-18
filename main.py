from autenticacao.auth import criar_usuario, verificar_login, resposta_da_pergunta_de_validacao, redefinir_senha_com_validacao


def main() -> None:
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
            criar_usuario(nome, senha)

        elif opcao == '2':
            nome = input('Digite o nome: ')
            senha = input('Digite a senha: ')

            if verificar_login(nome, senha):
                print(f'Login realizado com sucesso! Bem-vindo(a), {nome.strip().casefold()}')
            else:
                print('Nome ou senha incorretos.')
                
     
        elif opcao == '3':
            nome = input("digita o seu nome: ")
            pergunta = resposta_da_pergunta_de_validacao(nome)

            if pergunta is None:
                print("O Usuario nao foi encontrado")
                continue
            print(f"pergunta de validacao : {pergunta}")
            resposta = input('Resposta: ')
            nova_senha = input("Digita a nova senha: ")

            if redefinir_senha_com_validacao(
                nome,
                pergunta,
                resposta,
                nova_senha
             ):
                print('senha redefinida com sucesso')
            break
                
        elif opcao == '4':
            print("saindo do sistema")
            break
        


if __name__ == '__main__':
    main()



