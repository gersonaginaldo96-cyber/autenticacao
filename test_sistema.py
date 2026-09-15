import os

from autenticacao.auth import criar_usuario, redefinir_senha, verificar_login


def test_fluxo_cadastro_e_login():
    if os.path.exists('usuarios.db'):
        os.remove('usuarios.db')

    assert criar_usuario('Joao', '123456') is True
    assert verificar_login('Joao', '123456') is True
    assert verificar_login('Joao', 'senhaerrada') is False


def test_redefinir_senha():
    if os.path.exists('usuarios.db'):
        os.remove('usuarios.db')

    assert criar_usuario('Maria', 'senha_antiga') is True
    assert verificar_login('Maria', 'senha_antiga') is True

    assert redefinir_senha('Maria', 'senha_nova') is True
    assert verificar_login('Maria', 'senha_nova') is True
    assert verificar_login('Maria', 'senha_antiga') is False


def test_redefinir_senha_usuario_inexistente():
    if os.path.exists('usuarios.db'):
        os.remove('usuarios.db')

    assert redefinir_senha('UsuarioNaoExiste', 'nova_senha') is False
