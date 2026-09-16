from hashlib import sha256


from models.database import conectar_db


def gerar_hash(senha: str) -> str:
    return sha256(senha.encode('utf-8')).hexdigest()


def criar_usuario(nome: str, senha: str) -> bool:
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
        'INSERT INTO usuarios (nome, senha) VALUES (?, ?)',
        (nome_normalizado, gerar_hash(senha))
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
# redefinicao de senha colocar um limite de tentativas (rate limite)

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



__all__ = ['criar_usuario', 'verificar_login', 'verificar_usuario', 'gerar_hash', 'redefinir_senha']
