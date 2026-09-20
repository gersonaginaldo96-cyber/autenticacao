from hashlib import sha256
import random
from datetime import datetime

from models.database import conectar_db

# gerar o hash usando o bcyrpt junto
def gerar_hash(senha: str) -> str:
    return sha256(senha.encode('utf-8')).hexdigest()


def criar_usuario(
    nome: str,
    senha: str,
    pergunta: str | None = None,
    resposta: str | None = None,
) -> bool:
    nome_normalizado = nome.strip().casefold()

    if not nome_normalizado or not senha:
        print('Nome e senha são obrigatórios.')
        return False

    conn = conectar_db()
    cursor = conn.cursor()

    if cursor.execute('SELECT 1 FROM usuarios WHERE nome = ?', (nome_normalizado,)).fetchone():
        print('Usuário já existe.')
        conn.close()
        return False

    cursor.execute(
        '''
        INSERT INTO usuarios (
            nome, senha, pergunta_de_validacao,
            resposta_da_pergunta_de_validacao
        ) VALUES (?, ?, ?, ?)
        ''',
        (
            nome_normalizado,
            gerar_hash(senha),
            pergunta.strip() if pergunta else None,
            resposta.strip() if resposta else None,
        )
    )
    conn.commit()
    conn.close()
    print(f'Usuário {nome_normalizado} cadastrado com sucesso!')
    return True

# verificar login
def verificar_login(nome: str, senha: str) -> bool:
    nome_normalizado = nome.strip().casefold()

    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute('SELECT senha FROM usuarios WHERE nome = ?', (nome_normalizado,))
    resultado = cursor.fetchone()
    conn.close()

    if not resultado:
        return False

    senha_armazenada = resultado[0]
    return senha_armazenada == gerar_hash(senha)

# verificar se o usuário existe
def verificar_usuario(nome: str) -> bool:
    nome_normalizado = nome.strip().casefold()

    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute('SELECT 1 FROM usuarios WHERE nome = ?', (nome_normalizado,))
    resultado = cursor.fetchone()
    conn.close()

    return resultado is not None
# redefinicao de senha colocar um limite de tentativas (rate limite e bcrypt)
def gerar_senha_temp():
    return str(random.randint(10000,999999))# 6 digitos

# tratar questoes de validacao para poder passar para redifinicao
def pergunta_de_validacao(nome:str, pergunta:str, resposta: str) -> bool:
    nome_normalizado = nome.strip().casefold()
    pergunta_normalizada = pergunta.strip().casefold()
    resposta_normalizada = resposta.strip().casefold()

    conn = conectar_db()
    cursor = conn.cursor()

    cursor.execute(
        'SELECT pergunta_de_validacao, resposta_da_pergunta_de_validacao '
        'FROM usuarios WHERE nome = ?',
        (nome_normalizado,)
    )
    resultado = cursor.fetchone()
    conn.close()

    if not resultado:
        return False
    pergunta_salva, resposta_salva = resultado
    return (pergunta_salva.strip().casefold() == pergunta_normalizada and resposta_salva.strip().casefold() == resposta_normalizada)


def resposta_da_pergunta_de_validacao(nome: str,) ->str | None:
    nome_normalizado = nome.strip().casefold()

    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute(
        'SELECT pergunta_de_validacao FROM usuarios WHERE nome = ?',(nome_normalizado,)

    )
    resultado = cursor.fetchone()
    conn.close
    return resultado[0] if resultado else None


# redefinir senha atravez da validacao das informacoes
def redefinir_senha_com_validacao(nome: str, pergunta: str, resposta: str, nova_senha: str) -> bool:
    if not pergunta_de_validacao(nome, pergunta, resposta):
        print("pergunta ou respostas de validacao incorretas!")
        return False
    return redefinir_senha(nome, nova_senha) 

def redefinir_senha(nome: str, nova_senha: str) -> bool:
    nome_normalizado = nome.strip().casefold()

    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute('SELECT 1 FROM usuarios WHERE nome = ?', (nome_normalizado,))
    resultado = cursor.fetchone()

    if not resultado:
        print('Usuário não encontrado.')
        conn.close()
        return False

    cursor.execute(
        'UPDATE usuarios SET senha = ? WHERE nome = ?',
        (gerar_hash(nova_senha), nome_normalizado)
    )
    conn.commit()
    conn.close()
    print(f'Senha do usuário {nome_normalizado} redefinida com sucesso!')
    return True



__all__ = ['criar_usuario', 'verificar_login', 'verificar_usuario', 'gerar_hash', 'redefinir_senha','redefinir_senha_com_validacao','resposta_da_pergunta_de_validacao']
