from autenticacao.auth import criar_usuario, verificar_login,redefinir_senha


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
            nome = input('Digite o nome: ')
            nova_senha = input('Digite a nova senha: ')
            redefinir_senha(nome, nova_senha)

        elif opcao == '4':
            tentativas = 3
            while tentativas != 0:
                nome = input('Digite o nome para sair: ')
                senha = input('Digite a senha para sair: ')
                
                if verificar_login(nome, senha):
                    print('Saindo do sistema...')
                    return
                else:
                    tentativas -= 1
                    print(f'Senha incorreta. Tentativas restantes: {tentativas}')
            print('Número máximo de tentativas atingido. Saindo do sistema...')
        else:
            print('Opção inválida.')


if __name__ == '__main__':
    main()



