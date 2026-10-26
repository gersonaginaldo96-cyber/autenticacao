from autenticacao.auth import (
    criar_usuario,
    login_bloqueado,
    validar_senha,
    verificar_login,
)
from autenticacao.validacao import (
    redefinicao_bloqueada,
    redefinir_senha_com_codigo,
    solicitar_codigo_temporario,
)
from prompt_toolkit import prompt


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
            senha = prompt('Digite a senha: ', is_password=True)
            email = input('Digite o email: ')
            senha_valida, mensagem = validar_senha(senha)
            if not senha_valida or not nome.strip() or not email.strip():
                print(mensagem)
                continue
            criar_usuario(nome, senha, email)

        elif opcao == '2':
            nome = input('Digite o nome: ')
            senha = prompt('Digite a senha: ', is_password=True)

            if verificar_login(nome, senha):
                print(f'Login realizado com sucesso! Bem-vindo(a), {nome.strip().casefold()}')
            elif login_bloqueado(nome):
                print('Login bloqueado por excesso de tentativas. Tente novamente em 10 minutos.')
            else:
                print('Nome ou senha incorretos.')

        elif opcao == '3':
            nome = input("digita o seu nome: ")
            nome_normalizado = nome.strip().casefold()

            if redefinicao_bloqueada(nome_normalizado):
                print('Nome bloqueado devido a excessivas tentativas.')
                continue

            codigo = solicitar_codigo_temporario(nome_normalizado)
            if codigo is None:
                print('Não foi possível gerar um código para esse usuário.')
                continue
            print(f'verifica na caixa do seu email e copia o codigo temporario: {nome}')
            codigo_informado = input('Digite o código temporário: ')
            nova_senha = prompt('Digite a nova senha: ', is_password=True)

            if redefinir_senha_com_codigo(nome, codigo_informado, nova_senha):
                print('Senha redefinida com sucesso.')

        elif opcao == '4':
            print("saindo do sistema")
            break


if __name__ == '__main__':
    main()



