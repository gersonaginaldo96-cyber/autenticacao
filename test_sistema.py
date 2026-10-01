import sqlite3

import pytest

from autenticacao.auth import (
    criar_usuario,
    gerar_hash,
    gerar_senha_temp,
    redefinir_senha,
    verificar_hash,
    verificar_login,
    verificar_usuario,
)
from autenticacao.validacao import (
    redefinir_senha_com_codigo,
    solicitar_codigo_temporario,
)
from models.database import conectar_db
from main import main


@pytest.fixture
def banco_temporario(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    conectar_db().close()


def test_conectar_db_cria_as_tabelas(banco_temporario):
    conn = sqlite3.connect('usuarios.db')
    tabelas = {
        row[0]
        for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'"
        )
    }
    conn.close()

    assert {'usuarios', 'redefinir_pin'} <= tabelas
    conn = conectar_db()
    colunas_usuarios = {
        row[1] for row in conn.execute('PRAGMA table_info(usuarios)')
    }
    conn.close()
    assert not {
        'pergunta_de_validacao',
        'resposta_da_pergunta_de_validacao',
    } & colunas_usuarios


def test_gerar_hash_usa_salt_aleatorio_e_verifica_senha():
    primeiro_hash = gerar_hash('senha')
    segundo_hash = gerar_hash('senha')

    assert primeiro_hash != segundo_hash
    assert verificar_hash('senha', primeiro_hash) is True
    assert verificar_hash('senha', segundo_hash) is True
    assert verificar_hash('outra senha', primeiro_hash) is False


def test_gerar_senha_temp_gera_seis_digitos():
    senha = gerar_senha_temp()

    assert senha.isdigit()
    assert 100000 <= int(senha) <= 999999


def test_criar_usuario_normaliza_nome_e_impede_duplicata(banco_temporario):
    assert criar_usuario('  Joao  ', '123456@#$%^&*":><') is True
    assert criar_usuario('JOAO', 'outra senha') is False


def test_criar_usuario_rejeita_dados_obrigatorios(banco_temporario):
    assert criar_usuario('', 'senha') is False
    assert criar_usuario('usuario', '') is False


def test_menu_cadastro_pede_senha_com_caractere_especial(monkeypatch, capsys):
    entradas = iter(['1', 'usuario', 'senha123', '4'])
    monkeypatch.setattr('builtins.input', lambda _: next(entradas))

    main()

    saida = capsys.readouterr().out
    assert 'caracteres especiais' in saida
    assert 'Digite uma pergunta de validação:' not in saida


def test_cadastro_pede_apenas_nome_e_senha(
    monkeypatch, capsys, banco_temporario
):
    entradas = iter(['1', 'usuario', 'senha123@#', '4'])
    monkeypatch.setattr('builtins.input', lambda _: next(entradas))

    main()

    saida = capsys.readouterr().out
    assert 'cadastrado com sucesso' in saida
    assert 'pergunta' not in saida.casefold()


def test_verificar_login_com_senha_correta_e_incorreta(banco_temporario):
    criar_usuario('Joao', '123456@#$%^&*":><')

    assert verificar_login(' joao ', '123456@#$%^&*":><') is True
    assert verificar_login('Joao', 'senha errada') is False
    assert verificar_login('inexistente', '123456') is False


def test_login_bloqueia_apos_tres_senhas_incorretas(banco_temporario):
    criar_usuario('Joao', '123456@#$%^&*":><')

    for _ in range(3):
        assert verificar_login('Joao', 'senha errada') is False

    assert verificar_login('Joao', '123456@#$%^&*":><') is False


def test_verificar_usuario(banco_temporario):
    criar_usuario('Maria', 'senha forte@#')

    assert verificar_usuario(' maria ') is True
    assert verificar_usuario('inexistente') is False


def test_redefinir_senha(banco_temporario):
    criar_usuario('Maria', 'senha antiga@#')

    assert redefinir_senha(' maria ', 'senha nova') is True
    assert verificar_login('Maria', 'senha nova') is True
    assert verificar_login('Maria', 'senha antiga@#') is False


def test_redefinir_senha_rejeita_usuario_inexistente(banco_temporario):
    assert redefinir_senha('inexistente', 'senha nova') is False


def test_solicitar_codigo_temporario_salva_apenas_hash(banco_temporario):
    criar_usuario('Maria', 'senha antiga@#')

    codigo = solicitar_codigo_temporario(' maria ')
    conn = conectar_db()
    hash_salvo, criado_em = conn.execute(
        'SELECT tempo_hash, criado_em FROM redefinir_pin WHERE nome = ?',
        ('maria',),
    ).fetchone()
    conn.close()

    assert codigo is not None
    assert verificar_hash(codigo, hash_salvo) is True
    assert codigo != hash_salvo
    assert criado_em is not None


def test_solicitar_codigo_temporario_rejeita_usuario_inexistente(banco_temporario):
    assert solicitar_codigo_temporario('inexistente') is None


def test_redefinir_senha_com_codigo(banco_temporario):
    criar_usuario('Maria', 'senha antiga@#')
    codigo = solicitar_codigo_temporario('Maria')

    assert redefinir_senha_com_codigo('Maria', codigo, 'senha nova@#') is True
    assert verificar_login('Maria', 'senha nova@#') is True
    assert redefinir_senha_com_codigo('Maria', codigo, 'outra senha@#') is False


def test_redefinir_senha_com_codigo_rejeita_codigo_incorreto(banco_temporario):
    criar_usuario('Maria', 'senha antiga@#')
    solicitar_codigo_temporario('Maria')

    assert redefinir_senha_com_codigo(
        'Maria', '000000', 'senha nova@#'
    ) is False
    assert verificar_login('Maria', 'senha antiga@#') is True


def test_redefinicao_bloqueia_apos_tres_codigos_incorretos(banco_temporario):
    criar_usuario('Maria', 'senha antiga@#')
    codigo = solicitar_codigo_temporario('Maria')

    for _ in range(3):
        assert redefinir_senha_com_codigo(
            'Maria', '000000', 'senha nova@#'
        ) is False

    assert redefinir_senha_com_codigo(
        'Maria', codigo, 'senha nova@#'
    ) is False
    assert verificar_login('Maria', 'senha antiga@#') is True


def test_codigo_expirado_nao_redefine_senha(banco_temporario):
    criar_usuario('Maria', 'senha antiga@#')
    solicitar_codigo_temporario('Maria')
    conn = conectar_db()
    conn.execute(
        "UPDATE redefinir_pin SET criado_em = datetime('now', '-11 minutes') "
        'WHERE nome = ?',
        ('maria',),
    )
    conn.commit()
    conn.close()

    assert redefinir_senha_com_codigo(
        'Maria', '123456', 'senha nova@#'
    ) is False
    assert verificar_login('Maria', 'senha antiga@#') is True


def test_menu_redefine_senha_com_codigo_temporario(
    monkeypatch, capsys, banco_temporario
):
    criar_usuario('Maria', 'senha antiga@#')
    monkeypatch.setattr(
        'autenticacao.validacao.gerar_senha_temp', lambda: '123456'
    )
    entradas = iter(['3', 'Maria', '123456', 'senha nova@#', '4'])
    monkeypatch.setattr('builtins.input', lambda _: next(entradas))

    main()

    saida = capsys.readouterr().out
    assert 'Código temporário: 123456' in saida
    assert verificar_login('Maria', 'senha nova@#') is True


def test_main_sai_pela_opcao_quatro(monkeypatch, capsys):
    monkeypatch.setattr('builtins.input', lambda _: '4')

    main()

    assert 'saindo do sistema' in capsys.readouterr().out
