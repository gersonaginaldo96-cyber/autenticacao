"""Configuração e acesso ao banco SQLite do sistema."""

import sqlite3


def conectar_db():
    conn = sqlite3.connect('usuarios.db')
    conn.execute(
        '''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE,
            senha TEXT NOT NULL,
            pergunta_de_validacao TEXT,
            resposta_da_pergunta_de_validacao TEXT,
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ultima_alteracao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        '''
    )
    conn.execute(
        '''
        CREATE TABLE IF NOT EXISTS redefinir_pin(
            nome TEXT PRIMARY KEY,
            tempo_hash TEXT,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            tentativas INTEGER NOT NULL DEFAULT 0,
            bloqueado_ate TEXT
        )
        '''
    )

    colunas = {
        row[1] for row in conn.execute('PRAGMA table_info(redefinir_pin)')
    }
    if 'bloqueado_ate' not in colunas:
        conn.execute('ALTER TABLE redefinir_pin ADD COLUMN bloqueado_ate TEXT')

    conn.commit()
    return conn
