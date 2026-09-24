import secrets
import bcrypt

from models.database import conectar_db

# gerar o hash usando o bcyrpt junto
def gerar_hash(senha: str) -> str:
    return bcrypt.hashpw(senha.encode('utf-8'),bcrypt.gensalt()).decode('utf-8')


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
            print('usuario ja existente.')
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
                pergunta.strip() if pergunta else None,
                resposta.strip() if resposta else None,
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



