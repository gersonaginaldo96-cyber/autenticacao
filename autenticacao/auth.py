import secrets
from datetime import datetime, timedelta

import bcrypt

from models.database import conectar_db

LIMITE_TENTATIVAS_LOGIN = 3
TEMPO_BLOQUEIO_LOGIN = timedelta(minutes=10)


def gerar_hash(senha: str) -> str:
    """Gera um hash seguro de uma senha usando bcrypt com salt aleatório."""
    return bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verificar_hash(valor: str, hash_salvo: str) -> bool:
    """Compara um valor em texto puro com um hash bcrypt previamente salvo."""
    return bcrypt.checkpw(
        valor.encode('utf-8'),
        hash_salvo.encode('utf-8'),
    )
def validar_senha(senha: str) -> tuple[bool, str]:
        especiais = "@#$%^&*!><:.ºç'«&"

        if len(senha) < 8:
            return False, "A senha deve conter pelo meno 8 caracteres @!#ª:;_Ç?" 
        if not any(caractere in especiais for caractere in senha):
            return False, 'A senha deve conter caracteres especiais'
        return True, 'Senha valida'


def criar_usuario(
    nome: str,
    senha: str,
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
            print('nao foi possivel concluir o cadastro. verifica os dados e tente novamente.')
            return False
        valida,mensagem = validar_senha(senha)
        if not valida:
            print(mensagem)
            return False

        conn.execute(
            '''
            INSERT INTO usuarios (nome, senha) VALUES (?, ?)
            ''',
            (
                nome_normalizado,
                gerar_hash(senha),
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

    if login_bloqueado(nome_normalizado):
        return False

    conn = conectar_db()

    try:
        resultado = conn.execute(
            'SELECT senha FROM usuarios WHERE nome = ?',
            (nome_normalizado,)
        ).fetchone()

        if not resultado:
            return False

        senha_correta = bcrypt.checkpw(
            senha.encode('utf-8'),
            resultado[0].encode('utf-8'))

        if senha_correta:
            limpar_tentativas_login(nome_normalizado)
        else:
            registrar_tentativa_login(nome_normalizado)
        return senha_correta
    finally:
        conn.close()


def login_bloqueado(nome: str) -> bool:
    nome_normalizado = nome.strip().casefold()
    conn = conectar_db()
    try:
        resultado = conn.execute(
            'SELECT bloqueado_ate FROM login_bloqueios WHERE nome = ?',
            (nome_normalizado,),
        ).fetchone()

        if not resultado or not resultado[0]:
            return False

        bloqueado_ate = datetime.fromisoformat(resultado[0])
        if datetime.now() < bloqueado_ate:
            return True

        conn.execute(
            'DELETE FROM login_bloqueios WHERE nome = ?',
            (nome_normalizado,),
        )
        conn.commit()
        return False
    finally:
        conn.close()


def registrar_tentativa_login(nome: str) -> None:
    nome_normalizado = nome.strip().casefold()

    conn = conectar_db()
    try:
        resultado = conn.execute(
            'SELECT tentativas FROM login_bloqueios WHERE nome = ?',
            (nome_normalizado,),
        ).fetchone()
        tentativas = (resultado[0] if resultado else 0) + 1
        bloqueado_ate = None
        if tentativas >= LIMITE_TENTATIVAS_LOGIN:
            bloqueado_ate = (
                datetime.now() + TEMPO_BLOQUEIO_LOGIN
            ).isoformat()

        conn.execute(
            '''
            INSERT INTO login_bloqueios (nome, tentativas, bloqueado_ate)
            VALUES (?, ?, ?)
            ON CONFLICT(nome) DO UPDATE SET
                tentativas = excluded.tentativas,
                bloqueado_ate = excluded.bloqueado_ate
            ''',
            (nome_normalizado, tentativas, bloqueado_ate),
        )
        conn.commit()
    finally:
        conn.close()
# limpar tentativas de login
def limpar_tentativas_login(nome: str) -> None:
    nome_normalizado = nome.strip().casefold()
    conn = conectar_db()
    try:
        conn.execute('DELETE FROM login_bloqueios WHERE nome = ?', (nome_normalizado,))
        conn.commit()
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

# redefinicao de senha
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



