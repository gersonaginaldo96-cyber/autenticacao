import os
import secrets
import bcrypt
from cryptography.fernet import Fernet, InvalidToken

from models.database import conectar_db


def gerar_hash(senha: str) -> str:
    """Gera um hash seguro de uma senha usando bcrypt com salt aleatório."""
    return bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verificar_hash(valor: str, hash_salvo: str) -> bool:
    """Compara um valor em texto puro com um hash bcrypt previamente salvo."""
    return bcrypt.checkpw(
        valor.encode('utf-8'),
        hash_salvo.encode('utf-8'),
    )


def _cifrador() -> Fernet:
    """Retorna uma instância de Fernet a partir da variável de ambiente."""
    chave = os.environ.get('AUTH_ENCRYPTION_KEY')
    if not chave:
        raise RuntimeError(
            'A variável AUTH_ENCRYPTION_KEY deve conter uma chave Fernet.'
        )
    return Fernet(chave.encode('utf-8'))


def criptografar_texto(texto: str) -> str:
    return _cifrador().encrypt(texto.encode('utf-8')).decode('utf-8')


def descriptografar_texto(texto_criptografado: str) -> str:
    try:
        return _cifrador().decrypt(texto_criptografado.encode('utf-8')).decode('utf-8')
    except InvalidToken as erro:
        raise ValueError('Não foi possível descriptografar o valor.') from erro


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

    try:
        resultado = conn.execute(
            'SELECT 1 FROM usuarios WHERE nome = ?',
            (nome_normalizado,)
        ).fetchone()
        if resultado:
            print('sucedido.')
            return False

        conn.execute(
            '''
            INSERT INTO usuarios (
                nome, senha, pergunta_de_validacao,
                resposta_da_pergunta_de_validacao
            ) VALUES (?, ?, ?, ?)
            ''',
            (
                nome_normalizado,
                gerar_hash(senha),
                criptografar_texto(pergunta.strip()) if pergunta else None,
                gerar_hash(resposta.strip().casefold()) if resposta else None,
            )
        )
        conn.commit()

        print(f'Usuário {nome_normalizado} cadastrado com sucesso!')
        return True

    except Exception as erro:
        conn.rollback()
        print(f"erro de credenciais: {erro}")
        return False
    finally:
        conn.close()

# verificar login
def verificar_login(
        nome: str,
        senha: str
        )-> bool:
    nome_normalizado = nome.strip().casefold()
    conn = conectar_db()

    try:
        resultado = conn.execute(
            'SELECT senha FROM usuarios WHERE nome = ?',
            (nome_normalizado,)
        ).fetchone()

        if not resultado:
            return False

        return  bcrypt.checkpw(
            senha.encode('utf-8'),
            resultado[0].encode('utf-8'))
    
    finally:
        conn.close()

# verificar se o usuário existe
def verificar_usuario(nome: str) -> bool:
    nome_normalizado = nome.strip().casefold()
    conn = conectar_db()

    try:
        resultado = conn.execute(
            'SELECT 1 FROM usuarios WHERE nome = ?',
            (nome_normalizado,)
        ).fetchone()

        if not resultado:
            return False

        return True
    finally:
        conn.close()

# gerar senha temporaria
def gerar_senha_temp() -> str:
    return str(secrets.randbelow(900_000) + 100_000)


def redefinir_senha(nome: str, nova_senha: str) -> bool:
    nome_normalizado = nome.strip().casefold()

    conn = conectar_db()
    try:
        resultado = conn.execute(
            'SELECT 1 FROM usuarios WHERE nome = ?',
            (nome_normalizado,)
        ).fetchone()

        if not resultado:
            print('Usuário não encontrado.')
            return False

        conn.execute(
            'UPDATE usuarios SET senha = ? WHERE nome = ?',
            (gerar_hash(nova_senha), nome_normalizado)
        )
        conn.commit()
        print(f'Senha do usuário {nome_normalizado} redefinida com sucesso!')
        return True
    finally:
        conn.close()



