import sqlite3

import pytest

from autenticacao.auth import (
    criar_usuario,
    gerar_hash,
    gerar_senha_temp,
    pergunta_de_validacao,
    redefinir_senha,
    redefinir_senha_com_validacao,
    resposta_da_pergunta_de_validacao,
    verificar_login,
    verificar_usuario,
)
from models.database import conectar_db
from main import main


@pytest.fixture
def banco_temporario(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    conectar_db().close()


def adicionar_usuario_com_validacao(nome, senha, pergunta, resposta):
    conn = conectar_db()
    conn.execute(
        '''
        INSERT INTO usuarios (
            nome, senha, pergunta_de_validacao,
            resposta_da_pergunta_de_validacao
        ) VALUES (?, ?, ?, ?)
        ''',
        (nome.strip().casefold(), gerar_hash(senha), pergunta, resposta),
    )
    conn.commit()
    conn.close()


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


def test_gerar_hash_e_deterministico():
    assert gerar_hash('senha') == gerar_hash('senha')
    assert gerar_hash('senha') != gerar_hash('outra senha')


def test_gerar_senha_temp_gera_seis_digitos():
    senha = gerar_senha_temp()

    assert senha.isdigit()
    assert 10000 <= int(senha) <= 999999


def test_criar_usuario_normaliza_nome_e_impede_duplicata(banco_temporario):
    assert criar_usuario('  Joao  ', '123456') is True
    assert criar_usuario('JOAO', 'outra senha') is False


def test_criar_usuario_rejeita_dados_obrigatorios(banco_temporario):
    assert criar_usuario('', 'senha') is False
    assert criar_usuario('usuario', '') is False


def test_verificar_login_com_senha_correta_e_incorreta(banco_temporario):
    criar_usuario('Joao', '123456')

    assert verificar_login(' joao ', '123456') is True
    assert verificar_login('Joao', 'senha errada') is False
    assert verificar_login('inexistente', '123456') is False


def test_verificar_usuario(banco_temporario):
    criar_usuario('Maria', 'senha')

    assert verificar_usuario(' maria ') is True
    assert verificar_usuario('inexistente') is False


def test_resposta_da_pergunta_de_validacao_retorna_pergunta(banco_temporario):
    adicionar_usuario_com_validacao(
        'Maria', 'senha', 'Qual sua cidade?', 'Lisboa'
    )

    assert resposta_da_pergunta_de_validacao(' maria ') == 'Qual sua cidade?'
    assert resposta_da_pergunta_de_validacao('inexistente') is None


def test_pergunta_de_validacao_aceita_resposta_correta(banco_temporario):
    adicionar_usuario_com_validacao(
        'Maria', 'senha', 'Qual sua cidade?', 'Lisboa'
    )

    assert pergunta_de_validacao(
        ' maria ', ' qual sua cidade? ', ' lisboa '
    ) is True


def test_pergunta_de_validacao_rejeita_dados_incorretos(banco_temporario):
    adicionar_usuario_com_validacao(
        'Maria', 'senha', 'Qual sua cidade?', 'Lisboa'
    )

    assert pergunta_de_validacao('Maria', 'Pergunta errada', 'Lisboa') is False
    assert pergunta_de_validacao('Maria', 'Qual sua cidade?', 'Resposta errada') is False
    assert pergunta_de_validacao('inexistente', 'Qual sua cidade?', 'Lisboa') is False


def test_redefinir_senha(banco_temporario):
    criar_usuario('Maria', 'senha antiga')

    assert redefinir_senha(' maria ', 'senha nova') is True
    assert verificar_login('Maria', 'senha nova') is True
    assert verificar_login('Maria', 'senha antiga') is False


def test_redefinir_senha_rejeita_usuario_inexistente(banco_temporario):
    assert redefinir_senha('inexistente', 'senha nova') is False


def test_redefinir_senha_com_validacao(banco_temporario):
    adicionar_usuario_com_validacao(
        'Maria', 'senha antiga', 'Qual sua cidade?', 'Lisboa'
    )

    assert redefinir_senha_com_validacao(
        'Maria', 'Qual sua cidade?', 'Lisboa', 'senha nova'
    ) is True
    assert verificar_login('Maria', 'senha nova') is True


def test_redefinir_senha_com_validacao_rejeita_resposta_incorreta(
    banco_temporario,
):
    adicionar_usuario_com_validacao(
        'Maria', 'senha antiga', 'Qual sua cidade?', 'Lisboa'
    )

    assert redefinir_senha_com_validacao(
        'Maria', 'Qual sua cidade?', 'Resposta errada', 'senha nova'
    ) is False
    assert verificar_login('Maria', 'senha antiga') is True


def test_main_sai_pela_opcao_quatro(monkeypatch, capsys):
    monkeypatch.setattr('builtins.input', lambda _: '4')

    main()

    assert 'saindo do sistema' in capsys.readouterr().out
