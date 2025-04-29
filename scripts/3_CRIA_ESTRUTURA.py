import os
import win32security
import ntsecuritycon as con
from sqlalchemy import create_engine, Table, MetaData, select, update
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv
from pathlib import Path

# Caminho base onde as pastas serão criadas
base_path = r'D:\Arquivos'


# Carrega o .env que está um nível acima de src/
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

DATABASE_URI = os.getenv("DATABASE_URI")
if not DATABASE_URI:
    raise ValueError("DATABASE_URI não definida nas variáveis de ambiente.")

engine = create_engine(DATABASE_URI, echo=False)  # Desabilitar logging SQL

# Função para carregar dados das tabelas
def load_data(engine):
    meta = MetaData()
    meta.reflect(bind=engine)
    
    estruturas = Table('WeBotPastasEstruturas', meta, autoload_with=engine)
    pastas = Table('WeBotPastasPastas', meta, autoload_with=engine)
    permissoes = Table('WeBotPastasPermissoes', meta, autoload_with=engine)
    tipos_permissao = Table('WeBotPastastipos_permissao', meta, autoload_with=engine)
    grupos = Table('WeBotPastasgrupos', meta, autoload_with=engine)
    
    with engine.connect() as conn:
        estruturas_data = conn.execute(select(estruturas)).fetchall()
        pastas_data = conn.execute(select(pastas)).fetchall()
        permissoes_data = conn.execute(select(permissoes)).fetchall()
        tipos_permissao_data = conn.execute(select(tipos_permissao)).fetchall()
        grupos_data = conn.execute(select(grupos)).fetchall()
    
    return estruturas_data, pastas_data, permissoes_data, tipos_permissao_data, grupos_data

# Função para limpar o nome dos diretórios
def clean_directory_name(name):
    return name.replace('\r', '').replace('\n', '').strip()

# Função para encontrar o nome da pasta pelo ID
def find_pasta_name(pastas_data, id):
    for pasta in pastas_data:
        if pasta.id == id:
            return clean_directory_name(pasta.nomepasta)
    return None

# Função para construir o caminho completo de uma estrutura
def build_path(estrutura, estruturas_data, pastas_data, base_path):
    caminho_parts = []
    while estrutura.pai_id is not None:
        nome_pasta = find_pasta_name(pastas_data, estrutura.WeBotPastas_pasta_id)
        caminho_parts.insert(0, nome_pasta)
        estrutura = next(e for e in estruturas_data if e.id == estrutura.pai_id)
    
    nome_pasta = find_pasta_name(pastas_data, estrutura.WeBotPastas_pasta_id)
    caminho_parts.insert(0, nome_pasta)
    
    caminho = os.path.join(base_path, *caminho_parts)
    return caminho

# Função para criar pastas se não existirem
def create_folder_if_not_exists(path):
    try:
        os.makedirs(path, exist_ok=True)
    except PermissionError as e:
        print(f"Erro de permissão ao criar pasta {path}: {e}")
    except OSError as e:
        print(f"Erro ao criar pasta {path}: {e}")

# Função para verificar se o grupo existe
def group_exists(group_name):
    try:
        sid, domain, type = win32security.LookupAccountName(None, group_name)
        print(f"Grupo '{group_name}' encontrado. SID: {sid}, Domain: {domain}, Type: {type}")
        return True
    except win32security.error as e:
        if e.winerror == 1332:  # ERROR_NONE_MAPPED
            print(f"Grupo '{group_name}' não encontrado.")
            return False
        else:
            raise

# Função para ajustar permissões da pasta conforme tabela WeBotPastasPermissoes
def ajustar_permissoes(engine, caminho, estrutura_id):
    meta = MetaData()
    meta.reflect(bind=engine)
    permissoes = Table('WeBotPastasPermissoes', meta, autoload_with=engine)
    tipos_permissao = Table('WeBotPastastipos_permissao', meta, autoload_with=engine)
    grupos = Table('WeBotPastasgrupos', meta, autoload_with=engine)
    
    try:
        with engine.connect() as conn:
            permissoes_data = conn.execute(select(permissoes).where(permissoes.c.estrutura_id == estrutura_id)).fetchall()
            for permissao in permissoes_data:
                grupo = conn.execute(select(grupos).where(grupos.c.id == permissao.grupo_id)).fetchone()
                permissao_tipo = conn.execute(select(tipos_permissao).where(tipos_permissao.c.id == permissao.permissao_id)).fetchone()
                
                if grupo and permissao_tipo:
                    group_name = grupo.nome.strip()  # Remove espaços extras
                    print(f"Grupo encontrado: {group_name}")
                    if group_exists(group_name):
                        print(f"Grupo existe: {group_name}")
                        set_permissions(caminho, group_name, [permissao_tipo.nome])
                    else:
                        print(f"Grupo não encontrado: {group_name}")
    except SQLAlchemyError as e:
        print(f"Erro ao ajustar permissões: {e}")

# Função para definir permissões em uma pasta
def set_permissions(folder_path, group_name, permissions):
    print(f"Definindo permissões para {group_name} com {permissions} em {folder_path}")
    # Mapear as permissões de texto para os valores apropriados de NT
    permission_map = {
        "ReadAndExecute": con.FILE_GENERIC_READ | con.FILE_GENERIC_EXECUTE,
        "Modify": con.FILE_GENERIC_WRITE | con.FILE_GENERIC_READ | con.FILE_GENERIC_EXECUTE | con.DELETE,
        "FullControl": con.FILE_ALL_ACCESS
    }
    
    # Determinar permissões baseadas no texto
    permission_value = 0
    for perm in permissions:
        permission_value |= permission_map.get(perm, 0)

    # Obter o SID do grupo
    try:
        sid, domain, type = win32security.LookupAccountName(None, group_name)
        print(f"SID obtido para {group_name}: {sid}")

        # Obter a DACL atual da pasta
        sd = win32security.GetFileSecurity(folder_path, win32security.DACL_SECURITY_INFORMATION)
        dacl = sd.GetSecurityDescriptorDacl()

        # Criar nova DACL
        new_dacl = win32security.ACL()
        
        # Copiar ACEs da DACL existente para a nova DACL, exceto a do grupo alvo
        for i in range(dacl.GetAceCount()):
            ace = dacl.GetAce(i)
            if ace[2] != sid:
                new_dacl.AddAccessAllowedAce(win32security.ACL_REVISION, ace[1], ace[2])

        # Adicionar nova regra
        new_dacl.AddAccessAllowedAce(win32security.ACL_REVISION, permission_value, sid)
        sd.SetSecurityDescriptorDacl(1, new_dacl, 0)
        win32security.SetFileSecurity(folder_path, win32security.DACL_SECURITY_INFORMATION, sd)
        print(f'Permissões definidas para {group_name} com {permissions} em {folder_path}')
    except Exception as e:
        print(f"Erro ao definir permissões: {e}")

# Função para garantir a herança de permissões
def ensure_inheritance(path):
    try:
        sd = win32security.GetFileSecurity(path, win32security.DACL_SECURITY_INFORMATION)
        dacl = sd.GetSecurityDescriptorDacl()

        new_dacl = win32security.ACL()
        for i in range(dacl.GetAceCount()):
            ace = dacl.GetAce(i)
            new_dacl.AddAccessAllowedAceEx(win32security.ACL_REVISION, con.OBJECT_INHERIT_ACE | con.CONTAINER_INHERIT_ACE, ace[1], ace[2])
        
        sd.SetSecurityDescriptorDacl(1, new_dacl, 0)
        win32security.SetFileSecurity(path, win32security.DACL_SECURITY_INFORMATION, sd)
        print(f"Herança de permissões garantida para {path}")
    except Exception as e:
        print(f"Erro ao garantir herança de permissões: {e}")

# Função para criar a hierarquia básica de pastas e marcar como gerado
def criar_hierarquia_basica(engine):
    estruturas_data, pastas_data, permissoes_data, tipos_permissao_data, grupos_data = load_data(engine)
    meta = MetaData()
    meta.reflect(bind=engine)
    estruturas = Table('WeBotPastasEstruturas', meta, autoload_with=engine)
    
    with engine.connect() as conn:
        for estrutura in estruturas_data:
            if estrutura.auto == 'N' and estrutura.gerado == 'N':
                caminho_completo = build_path(estrutura, estruturas_data, pastas_data, base_path)
                create_folder_if_not_exists(caminho_completo)
                
                # Limpar permissões padrão
                try:
                    sd = win32security.GetFileSecurity(caminho_completo, win32security.DACL_SECURITY_INFORMATION)
                    dacl = sd.GetSecurityDescriptorDacl()
                    new_dacl = win32security.ACL()
                    sd.SetSecurityDescriptorDacl(1, new_dacl, 0)
                    win32security.SetFileSecurity(caminho_completo, win32security.DACL_SECURITY_INFORMATION, sd)
                    print(f'Permissões padrão removidas para {caminho_completo}')
                except Exception as e:
                    print(f"Erro ao limpar permissões padrão: {e}")

                ajustar_permissoes(engine, caminho_completo, estrutura.id)
                ensure_inheritance(caminho_completo)  # Garantir herança de permissões
                
                # Atualizar a coluna gerado para 'S'
                stmt = update(estruturas).where(estruturas.c.id == estrutura.id).values(gerado='S')
                result = conn.execute(stmt)
                conn.commit()

# Executar a criação da hierarquia básica
criar_hierarquia_basica(engine)
print("Permissões ajustadas com sucesso.")
