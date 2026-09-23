from hashlib import sha256
import random
from datetime import datetime, timedelta

from models.database import conectar_db

LIMITE_TENTATIVAS = 3
TEMPO_BLOQUEIO = timedelta(minutes=5)

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

    try:
        resultado = cursor.execute('SELECT 1 FROM usuarios WHERE nome = ?', (nome_normalizado,)).fetchone()
        if resultado:
            print('usuario ja existente.')
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
    conn = conectar_db
    try:
        resultado = conn.execute('SELECT senha FROM usuarios WHERE nome = ?', (nome_normalizado,)).fetchone()
        return  resultado is not None
    except Exception as erro:
        print(f'erro de credeciais: {erro}')
        return False
    finally:
        senha_armazenada = resultado[0]
        return senha_armazenada == gerar_hash(senha)

# verificar se o usuário existe
def verificar_usuario(nome: str) -> bool:
    nome_normalizado = nome.strip().casefold()
    conn = conectar_db()

    try:
        resultado = conn.execute(
            'SELECT 1 FROM usuarios WHERE nome = ?',
            (nome_normalizado,)
        ).fetchone()
        return resultado is not None
    except Exception as erro:
        print(f'Erro ao verificar usuário: {erro}')
        return False
    finally:
        conn.close()

# gerar senha temporaria
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

# respostas da pergunta de validacao
def resposta_da_pergunta_de_validacao(nome: str,) ->str | None:
    nome_normalizado = nome.strip().casefold()

    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute(
        'SELECT pergunta_de_validacao FROM usuarios WHERE nome = ?',(nome_normalizado,)

    )
    resultado = cursor.fetchone()
    conn.close()
    return resultado[0] if resultado else None


def redefinicao_bloqueada(nome: str) -> bool:
    conn = conectar_db()
    resultado = conn.execute(
        'SELECT bloqueado_ate FROM redefinir_pin WHERE nome = ?',
        (nome,)
    ).fetchone()

    if not resultado or not resultado[0]:
        conn.close()
        return False

    bloqueado_ate = datetime.fromisoformat(resultado[0])
    if datetime.now() < bloqueado_ate:
        conn.close()
        return True

    conn.execute(
        'UPDATE redefinir_pin SET tentativas = 0, bloqueado_ate = NULL WHERE nome = ?',
        (nome,)
    )
    conn.commit()
    conn.close()
    return False


def registrar_tentativa_incorreta(nome: str) -> None:
    conn = conectar_db()
    resultado = conn.execute(
        'SELECT tentativas FROM redefinir_pin WHERE nome = ?',
        (nome,)
    ).fetchone()
    tentativas = (resultado[0] if resultado else 0) + 1
    bloqueado_ate = None

    if tentativas >= LIMITE_TENTATIVAS:
        bloqueado_ate = (datetime.now() + TEMPO_BLOQUEIO).isoformat()

    conn.execute(
        '''
        INSERT INTO redefinir_pin (nome, tentativas, bloqueado_ate)
        VALUES (?, ?, ?)
        ON CONFLICT(nome) DO UPDATE SET
            tentativas = excluded.tentativas,
            bloqueado_ate = excluded.bloqueado_ate
        ''',
        (nome, tentativas, bloqueado_ate),
    )
    conn.commit()
    conn.close()


def limpar_tentativas(nome: str) -> None:
    conn = conectar_db()
    conn.execute(
        'DELETE FROM redefinir_pin WHERE nome = ?',
        (nome,)
    )
    conn.commit()
    conn.close()


# redefinir senha atravez da validacao das informacoes e bloquear apos 3 tentativas 
def redefinir_senha_com_validacao(nome: str, pergunta: str, resposta: str, nova_senha: str) -> bool:
    nome_normalizado = nome.strip().casefold()

    if redefinicao_bloqueada(nome_normalizado):
        print('Muitas tentativas. Tente novamente mais tarde.')
        return False

    if not pergunta_de_validacao(nome, pergunta, resposta):
        registrar_tentativa_incorreta(nome_normalizado)
        print("pergunta ou respostas de validacao incorretas!")
        return False

    limpar_tentativas(nome_normalizado)
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
