"""Fluxo de validação da pergunta secreta e controle de bloqueio por tentativas.

Este módulo garante que a recuperação de senha só ocorra quando a pergunta e a
resposta fornecidas pelo usuário conferem com o registro salvo. Também controla
um bloqueio temporário após várias tentativas incorretas.
"""

from datetime import datetime, timedelta

from models.database import conectar_db
from autenticacao.auth import (
    descriptografar_texto,
    redefinir_senha,
    verificar_hash,
)

LIMITE_TENTATIVAS = 3
TEMPO_BLOQUEIO = timedelta(minutes=5)


def pergunta_de_validacao(nome: str, pergunta: str, resposta: str) -> bool:
    """Valida se a pergunta e a resposta informadas correspondem ao cadastro."""
    nome_normalizado = nome.strip().casefold()
    pergunta_normalizada = pergunta.strip().casefold()
    resposta_normalizada = resposta.strip().casefold()

    conn = conectar_db()

    try:
        resultado = conn.execute(
            'SELECT pergunta_de_validacao, resposta_da_pergunta_de_validacao '
            'FROM usuarios WHERE nome = ?',
            (nome_normalizado,)
        ).fetchone()

        if not resultado:
            return False

        pergunta_salva, resposta_salva = resultado
        if not pergunta_salva or not resposta_salva:
            return False

        try:
            pergunta_descriptografada = descriptografar_texto(pergunta_salva)
        except (RuntimeError, ValueError):
            return False

        return (
            pergunta_descriptografada.strip().casefold() == pergunta_normalizada
            and verificar_hash(resposta_normalizada, resposta_salva)
        )
    finally:
        conn.close()


def resposta_da_pergunta_de_validacao(nome: str) -> str | None:
    """Busca a pergunta gravada para um usuário e a retorna em texto legível."""
    nome_normalizado = nome.strip().casefold()

    conn = conectar_db()
    try:
        resultado = conn.execute(
            'SELECT pergunta_de_validacao FROM usuarios WHERE nome = ?',
            (nome_normalizado,)
        ).fetchone()
        if not resultado or not resultado[0]:
            return None

        try:
            return descriptografar_texto(resultado[0])
        except (RuntimeError, ValueError):
            return None
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
    conn = conectar_db()
    try:
        conn.execute(
            'DELETE FROM redefinir_pin WHERE nome = ?',
            (nome,)
        )
        conn.commit()
    finally:
        conn.close()


def validar_redefinicao(nome: str, pergunta: str, resposta: str) -> bool:
    """Executa todo o fluxo de validação de recuperação de senha."""
    nome_normalizado = nome.strip().casefold()

    if redefinicao_bloqueada(nome_normalizado):
        print('Muitas tentativas. Tente novamente mais tarde.')
        return False

    if not pergunta_de_validacao(nome, pergunta, resposta):
        registrar_tentativa_incorreta(nome_normalizado)
        print('pergunta ou respostas de validacao incorretas!')
        return False

    return True


def redefinir_senha_com_validacao(
    nome: str,
    pergunta: str,
    resposta: str,
    nova_senha: str,
) -> bool:
    """Valida a recuperação e, em seguida, altera a senha do usuário."""
    nome_normalizado = nome.strip().casefold()

    if not validar_redefinicao(nome, pergunta, resposta):
        return False

    limpar_tentativas(nome_normalizado)
    return redefinir_senha(nome, nova_senha)


__all__ = [
    'pergunta_de_validacao',
    'resposta_da_pergunta_de_validacao',
    'redefinicao_bloqueada',
    'registrar_tentativa_incorreta',
    'limpar_tentativas',
    'validar_redefinicao',
    'redefinir_senha_com_validacao',
]
