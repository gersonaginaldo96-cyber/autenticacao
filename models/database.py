import sqlite3


def conectar_db():
    conn = sqlite3.connect('usuarios.db')
    conn.execute(
        '''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE,
            senha TEXT NOT NULL,
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ultima_alteracao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        '''
    )
    conn.commit()
    return conn
