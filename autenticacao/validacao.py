"""Fluxo de recuperação por código temporário e controle de tentativas."""

from datetime import datetime, timedelta

from autenticacao.auth import (
    gerar_hash,
    gerar_senha_temp,
    validar_senha,
    verificar_hash,
)
from models.database import conectar_db

LIMITE_TENTATIVAS = 3
TEMPO_BLOQUEIO = timedelta(minutes=5)
VALIDADE_CODIGO = timedelta(minutes=10)


def solicitar_codigo_temporario(nome: str) -> str | None:
    """Gera um código para um usuário existente e o salva como hash."""
    nome_normalizado = nome.strip().casefold()

    if redefinicao_bloqueada(nome_normalizado):
        return None

    conn = conectar_db()
    try:
        resultado = conn.execute(
            'SELECT 1 FROM usuarios WHERE nome = ?',
            (nome_normalizado,)
        ).fetchone()

        if not resultado:
            return None

        codigo = gerar_senha_temp()
        conn.execute(
            '''
            INSERT INTO redefinir_pin (
                nome, tempo_hash, criado_em, tentativas, bloqueado_ate
            ) VALUES (?, ?, ?, 0, NULL)
            ON CONFLICT(nome) DO UPDATE SET
                tempo_hash = excluded.tempo_hash,
                criado_em = excluded.criado_em,
                tentativas = 0,
                bloqueado_ate = NULL
            ''',
            (nome_normalizado, gerar_hash(codigo), datetime.now().isoformat()),
        )
        conn.commit()
        return codigo
    finally:
        conn.close()


def redefinir_senha_com_codigo(
    nome: str,
    codigo: str,
    nova_senha: str,
) -> bool:
    """Redefine a senha se o código estiver correto, válido e não expirado."""
    nome_normalizado = nome.strip().casefold()
    
    senha_valida, mensagem = validar_senha(nova_senha)
    if not senha_valida:
        print(mensagem)
        return False

    if redefinicao_bloqueada(nome_normalizado):
        print('Muitas tentativas. Tente novamente mais tarde.')
        return False

    conn = conectar_db()
    try:
        resultado = conn.execute(
            'SELECT tempo_hash, criado_em FROM redefinir_pin WHERE nome = ?',
            (nome_normalizado,)
        ).fetchone()

        if not resultado:
            return False

        hash_codigo, criado_em = resultado
    finally:
        conn.close()

    if datetime.now() - datetime.fromisoformat(criado_em) > VALIDADE_CODIGO:
        limpar_tentativas(nome_normalizado)
        print('O código temporário expirou. Solicite outro código.')
        return False

    if not verificar_hash(codigo.strip(), hash_codigo):
        registrar_tentativa_incorreta(nome_normalizado)
        print('Código temporário incorreto.')
        return False

    conn = conectar_db()
    try:
        resultado = conn.execute(
            'UPDATE usuarios SET senha = ? WHERE nome = ?',
            (gerar_hash(nova_senha), nome_normalizado),
        )
        if resultado.rowcount == 0:
            conn.rollback()
            return False

        conn.execute(
            'DELETE FROM redefinir_pin WHERE nome = ?',
            (nome_normalizado,),
        )
        conn.commit()
        return True
    finally:
        conn.close()


def redefinicao_bloqueada(nome: str) -> bool:
    """Verifica se o nome está bloqueado e libera o acesso quando o prazo expira."""
    conn = conectar_db()
    try:
        resultado = conn.execute(
            'SELECT bloqueado_ate FROM redefinir_pin WHERE nome = ?',
            (nome,)
        ).fetchone()

        if not resultado or not resultado[0]:
            return False

        bloqueado_ate = datetime.fromisoformat(resultado[0])
        if datetime.now() < bloqueado_ate:
            return True

        conn.execute(
            'UPDATE redefinir_pin SET tentativas = 0, bloqueado_ate = NULL WHERE nome = ?',
            (nome,)
        )
        conn.commit()
        return False
    finally:
        conn.close()


def registrar_tentativa_incorreta(nome: str) -> None:
    """Incrementa o contador de falhas e bloqueia temporariamente após o limite."""
    nome = nome.strip().casefold()
    conn = conectar_db()
    try:
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
    finally:
        conn.commit()
        conn.close()


def limpar_tentativas(nome: str) -> None:
    """Remove o registro de bloqueio e tentativas do usuário após sucesso."""
    nome = nome.strip().casefold()
    conn = conectar_db()
    try:
        conn.execute(
            'DELETE FROM redefinir_pin WHERE nome = ?',
            (nome,)
        )
        conn.commit()
    finally:
        conn.close()


__all__ = [
    'solicitar_codigo_temporario',
    'redefinir_senha_com_codigo',
    'redefinicao_bloqueada',
    'registrar_tentativa_incorreta',
    'limpar_tentativas',
]
