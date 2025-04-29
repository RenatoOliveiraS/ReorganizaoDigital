import os
import win32security
import ntsecuritycon as con
from sqlalchemy import create_engine, Table, MetaData, select, insert, update, and_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from pathlib import Path

# Caminho base onde as pastas serão criadas
base_path = r'D:\Arquivos'

# Configuração da conexão com o banco de dados
# Carrega o .env que está um nível acima de src/
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

DATABASE_URI = os.getenv("DATABASE_URI")
if not DATABASE_URI:
    raise ValueError("DATABASE_URI não definida nas variáveis de ambiente.")

engine = create_engine(DATABASE_URI, echo=False)  # echo=False para desabilitar o logging SQL

# Configuração da sessão
Session = sessionmaker(bind=engine)

# Função para carregar dados das tabelas
def carregar_dados():
    try:
        meta = MetaData()
        meta.reflect(bind=engine)

        estruturas = Table('WeBotPastasEstruturas', meta, autoload_with=engine)
        pastas = Table('WeBotPastasPastas', meta, autoload_with=engine)
        empresas = Table('WeBotPastasEmpresas', meta, autoload_with=engine)
        empresas_estruturas = Table('WeBotPastasEmpresasEstruturas', meta, autoload_with=engine)
        permissoes = Table('WeBotPastasPermissoes', meta, autoload_with=engine)
        tipos_permissao = Table('WeBotPastastipos_permissao', meta, autoload_with=engine)
        grupos = Table('WeBotPastasgrupos', meta, autoload_with=engine)

        with Session() as session:
            print("Conectado ao banco de dados")
            estruturas_data = session.execute(select(estruturas)).fetchall()
            pastas_data = session.execute(select(pastas)).fetchall()
            empresas_data = session.execute(select(empresas)).fetchall()
            permissoes_data = session.execute(select(permissoes)).fetchall()
            tipos_permissao_data = session.execute(select(tipos_permissao)).fetchall()
            grupos_data = session.execute(select(grupos)).fetchall()

        return estruturas_data, pastas_data, empresas_data, empresas_estruturas, permissoes_data, tipos_permissao_data, grupos_data
    except SQLAlchemyError as e:
        print(f"Erro ao carregar dados: {e}")
        return [], [], [], [], [], [], []

# Função para limpar o nome dos diretórios
def limpar_nome_diretorio(nome):
    if nome is not None:
        return nome.replace('\r', '').replace('\n', '').strip()
    else:
        return ''

# Função para encontrar o nome da pasta pelo ID
def encontrar_nome_pasta(pastas_data, id_pasta):
    for pasta in pastas_data:
        if pasta.id == id_pasta:
            return limpar_nome_diretorio(pasta.nomepasta)
    return None

# Função para construir o caminho completo de uma estrutura
def construir_caminho(estrutura, estruturas_data, pastas_data, base_path, empresa_nome=None):
    partes_caminho = []
    estrutura_atual = estrutura
    while estrutura_atual and estrutura_atual.pai_id is not None:
        nome_pasta = encontrar_nome_pasta(pastas_data, estrutura_atual.WeBotPastas_pasta_id)
        if nome_pasta and nome_pasta != 'AutoPastaWebot - Empresas':
            partes_caminho.insert(0, nome_pasta)
        estrutura_atual = next((e for e in estruturas_data if e.id == estrutura_atual.pai_id), None)

    if estrutura_atual:
        nome_pasta = encontrar_nome_pasta(pastas_data, estrutura_atual.WeBotPastas_pasta_id)
        if nome_pasta and nome_pasta != 'AutoPastaWebot - Empresas':
            partes_caminho.insert(0, nome_pasta)

    # Inserir 'Empresas' e 'Arquivo Digital' se não estiverem presentes
    if 'Empresas' not in partes_caminho:
        partes_caminho.insert(0, 'Empresas')
    if 'Arquivo Digital' not in partes_caminho:
        partes_caminho.insert(0, 'Arquivo Digital')

    # Inserir o nome da empresa após 'Empresas'
    if empresa_nome:
        try:
            index_empresas = partes_caminho.index('Empresas')
            partes_caminho.insert(index_empresas + 1, empresa_nome)
        except ValueError:
            partes_caminho.insert(0, empresa_nome)

    caminho = os.path.join(base_path, *partes_caminho)
    return caminho

# Função para criar pastas se não existirem
def criar_pasta_se_nao_existir(caminho):
    try:
        if not os.path.exists(caminho):
            os.makedirs(caminho)
            print(f'Pasta criada: {caminho}')
        else:
            print(f'Pasta já existe: {caminho}')
    except OSError as e:
        print(f"Erro ao criar pasta {caminho}: {e}")

# Função para verificar se o grupo existe
def grupo_existe(group_name):
    try:
        sid, domain, type = win32security.LookupAccountName(None, group_name)
        #print(f"Grupo '{group_name}' encontrado. SID: {sid}, Domain: {domain}, Type: {type}")
        return True
    except win32security.error as e:
        if e.winerror == 1332:  # ERROR_NONE_MAPPED
            #print(f"Grupo '{group_name}' não encontrado.")
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
                    #print(f"Grupo encontrado: {group_name}")
                    if grupo_existe(group_name):
                        #print(f"Grupo existe: {group_name}")
                        definir_permissoes(caminho, group_name, [permissao_tipo.nome])  # Alteração aqui
                    else:
                        print(f"Grupo não encontrado: {group_name}")
    except SQLAlchemyError as e:
        print(f"Erro ao ajustar permissões: {e}")


# Função para definir permissões em uma pasta
def definir_permissoes(caminho_pasta, nome_grupo, permissoes):
    #print(f"Definindo permissões para {nome_grupo} com {permissoes} em {caminho_pasta}")
    
    # Mapear as permissões de texto para os valores apropriados de NT
    mapa_permissoes = {
        "ReadAndExecute": con.FILE_GENERIC_READ | con.FILE_GENERIC_EXECUTE,
        "Modify": con.FILE_GENERIC_WRITE | con.FILE_GENERIC_READ | con.FILE_GENERIC_EXECUTE | con.DELETE,
        "FullControl": con.FILE_ALL_ACCESS
    }
    
    # Determinar permissões baseadas no texto
    valor_permissao = 0
    for permissao in permissoes:
        valor_permissao |= mapa_permissoes.get(permissao, 0)

    # Obter o SID do grupo
    try:
        sid, dominio, tipo = win32security.LookupAccountName(None, nome_grupo)
        #print(f"SID obtido para {nome_grupo}: {sid}")

        # Obter a DACL atual da pasta
        sd = win32security.GetFileSecurity(caminho_pasta, win32security.DACL_SECURITY_INFORMATION)
        dacl = sd.GetSecurityDescriptorDacl()

        # Criar nova DACL
        nova_dacl = win32security.ACL()
        
        # Copiar ACEs da DACL existente para a nova DACL, exceto a do grupo alvo
        for i in range(dacl.GetAceCount()):
            ace = dacl.GetAce(i)
            if ace[2] != sid:
                nova_dacl.AddAccessAllowedAce(win32security.ACL_REVISION, ace[1], ace[2])

        # Adicionar nova regra de permissão
        nova_dacl.AddAccessAllowedAce(win32security.ACL_REVISION, valor_permissao, sid)
        sd.SetSecurityDescriptorDacl(1, nova_dacl, 0)
        win32security.SetFileSecurity(caminho_pasta, win32security.DACL_SECURITY_INFORMATION, sd)
        #print(f'Permissões definidas para {nome_grupo} com {permissoes} em {caminho_pasta}')
    except Exception as e:
        print(f"Erro ao definir permissões: {e}")


# Função para garantir a herança de permissões
def garantir_heranca(caminho):
    try:
        sd = win32security.GetFileSecurity(caminho, win32security.DACL_SECURITY_INFORMATION)
        dacl = sd.GetSecurityDescriptorDacl()

        nova_dacl = win32security.ACL()
        for i in range(dacl.GetAceCount()):
            ace = dacl.GetAce(i)
            nova_dacl.AddAccessAllowedAceEx(win32security.ACL_REVISION, con.OBJECT_INHERIT_ACE | con.CONTAINER_INHERIT_ACE, ace[1], ace[2])
        
        sd.SetSecurityDescriptorDacl(1, nova_dacl, 0)
        win32security.SetFileSecurity(caminho, win32security.DACL_SECURITY_INFORMATION, sd)
        #print(f"Herança de permissões garantida para {caminho}")
    except Exception as e:
        print(f"Erro ao garantir herança de permissões: {e}")

# Função para substituir placeholders no caminho
def substituir_placeholders(caminho, valores_substituicao):
    for placeholder, valor in valores_substituicao.items():
        caminho = caminho.replace(placeholder, valor)
    return caminho

# Função para preencher a tabela de hierarquia de pastas por empresa
def preencher_tabela_empresas_estruturas(empresas_data, estruturas_data, pastas_data):
    meta = MetaData()
    meta.reflect(bind=engine)
    empresas_estruturas = Table('WeBotPastasEmpresasEstruturas', meta, autoload_with=engine)
    empresas = Table('WeBotPastasEmpresas', meta, autoload_with=engine)

    try:
        with Session() as session:
            # Buscar empresas com 'gerado' == 'N'
            empresas_nao_geradas = session.execute(
                select(empresas).where(empresas.c.gerado == 'N')
            ).fetchall()

            for empresa in empresas_nao_geradas:
                
                for estrutura in estruturas_data:
                    if estrutura.auto == 'S' and estrutura.WeBotPastas_pasta_id == 102:
                        caminho_pai = construir_caminho(estrutura, estruturas_data, pastas_data, base_path, limpar_nome_diretorio(empresa.nomepasta))
                        nivel = 1

                        existe = session.execute(select(empresas_estruturas).where(
                            and_(
                                empresas_estruturas.c.empresa_id == empresa.id,
                                empresas_estruturas.c.estrutura_id == estrutura.id,
                                empresas_estruturas.c.caminho_completo == caminho_pai
                            )
                        )).fetchone()

                        if not existe:
                            ins_stmt = insert(empresas_estruturas).values(
                                empresa_id=empresa.id,
                                estrutura_id=estrutura.id,
                                nomepasta=limpar_nome_diretorio(empresa.nomepasta),
                                caminho_completo=caminho_pai,
                                nivel=nivel,
                                gerado='N'
                            )
                            session.execute(ins_stmt)

                        # Chamar criar_subpastas com a estrutura atual
                        criar_subpastas(session, empresa, estruturas_data, pastas_data, estrutura, caminho_pai, nivel)

                # Atualizar a empresa para 'gerado' == 'S' após a criação das pastas
                session.execute(
                    update(empresas).where(empresas.c.id == empresa.id).values(gerado='S')
                )
            session.commit()
    except SQLAlchemyError as e:
        print(f"Erro ao preencher a tabela de hierarquia de pastas por empresa: {e}")
        session.rollback()


def criar_subpastas(session, empresa, estruturas_data, pastas_data, estrutura_pai, caminho_pai, nivel_atual, visitados=None):
    if visitados is None:
        visitados = set()

    # Verificar se já visitamos esta estrutura para evitar loops
    if estrutura_pai.id in visitados:
        print(f"Loop detectado na estrutura ID {estrutura_pai.id}")
        return
    visitados.add(estrutura_pai.id)

    for child_estrutura in estruturas_data:
        if child_estrutura.pai_id == estrutura_pai.id:
            id_pasta_child = child_estrutura.WeBotPastas_pasta_id
            nome_pasta_child = encontrar_nome_pasta(pastas_data, id_pasta_child)

            # Garantir que o nome da pasta não seja None antes de continuar
            if not nome_pasta_child:
                print(f"Nome da pasta não encontrado para o ID {id_pasta_child}. Pulando esta estrutura.")
                continue  # Pula para a próxima estrutura se o nome da pasta for inválido

            nivel_novo = nivel_atual + 1
            child_path = os.path.join(caminho_pai, nome_pasta_child)

            existe = session.execute(select(empresas_estruturas).where(
                and_(
                    empresas_estruturas.c.empresa_id == empresa.id,
                    empresas_estruturas.c.estrutura_id == child_estrutura.id,
                    empresas_estruturas.c.caminho_completo == child_path
                )
            )).fetchone()

            # Verificar se estamos no nível ANO (não criar a pasta com o placeholder, substituir pelo ano real)
            if id_pasta_child == 114:  # AutoPastaWebot - ANO
                anos = ['2025']  # Ajuste conforme necessário
                for ano in anos:
                    # Substituir o placeholder ANO antes de criar a pasta
                    child_path_real = child_path.replace('AutoPastaWebot - ANO', ano)

                    # Verificar se já existe o registro para o caminho real
                    existe = session.execute(select(empresas_estruturas).where(
                        and_(
                            empresas_estruturas.c.empresa_id == empresa.id,
                            empresas_estruturas.c.estrutura_id == child_estrutura.id,
                            empresas_estruturas.c.caminho_completo == child_path_real
                        )
                    )).fetchone()

                    if not existe:
                        ins_stmt = insert(empresas_estruturas).values(
                            empresa_id=empresa.id,
                            estrutura_id=child_estrutura.id,
                            nomepasta=nome_pasta_child,
                            caminho_completo=child_path_real,
                            nivel=nivel_novo,
                            gerado='N'
                        )
                        session.execute(ins_stmt)

                    # Criar fisicamente a pasta com o nome substituído (real)
                    criar_pasta_se_nao_existir(child_path_real)

                    # Continuar criando subpastas para este ano
                    criar_subpastas(session, empresa, estruturas_data, pastas_data, child_estrutura, child_path_real, nivel_novo, visitados.copy())

            # Verificar se estamos no nível MÊS (não criar a pasta com o placeholder, substituir pelo mês real)
            elif id_pasta_child == 115:  # AutoPastaWebot - MÊS
                meses = [f'{i:02d}' for i in range(1, 13)]
                for mes in meses:
                    # Substituir o placeholder MÊS antes de criar a pasta
                    child_path_real = child_path.replace('AutoPastaWebot - MÊS', mes)

                    # Verificar se já existe o registro para o caminho real
                    existe = session.execute(select(empresas_estruturas).where(
                        and_(
                            empresas_estruturas.c.empresa_id == empresa.id,
                            empresas_estruturas.c.estrutura_id == child_estrutura.id,
                            empresas_estruturas.c.caminho_completo == child_path_real
                        )
                    )).fetchone()

                    if not existe:
                        ins_stmt = insert(empresas_estruturas).values(
                            empresa_id=empresa.id,
                            estrutura_id=child_estrutura.id,
                            nomepasta=nome_pasta_child,
                            caminho_completo=child_path_real,
                            nivel=nivel_novo,
                            gerado='N'
                        )
                        session.execute(ins_stmt)

                    # Criar fisicamente a pasta com o nome substituído (real)
                    criar_pasta_se_nao_existir(child_path_real)

                    # Continuar criando subpastas para este mês
                    criar_subpastas(session, empresa, estruturas_data, pastas_data, child_estrutura, child_path_real, nivel_novo, visitados.copy())
            
            # Se não for ANO ou MÊS, criar a pasta normalmente
            else:
                if not existe:
                    ins_stmt = insert(empresas_estruturas).values(
                        empresa_id=empresa.id,
                        estrutura_id=child_estrutura.id,
                        nomepasta=nome_pasta_child,
                        caminho_completo=child_path,
                        nivel=nivel_novo,
                        gerado='N'
                    )
                    session.execute(ins_stmt)

                # Criar a pasta fisicamente (sem placeholders)
                criar_pasta_se_nao_existir(child_path)

                # Continuar criando as subpastas
                criar_subpastas(session, empresa, estruturas_data, pastas_data, child_estrutura, child_path, nivel_novo, visitados.copy())

def criar_estrutura_pastas():
    meta = MetaData()
    meta.reflect(bind=engine)
    empresas_estruturas = Table('WeBotPastasEmpresasEstruturas', meta, autoload_with=engine)

    try:
        with Session() as session:
            # Buscar registros onde gerado == 'N' (sem filtrar por empresa específica)
            estruturas_data = session.execute(
                select(empresas_estruturas)
                .where(empresas_estruturas.c.gerado == 'N')
                .order_by(empresas_estruturas.c.nivel)
            ).fetchall()
            #print(f"Estruturas a serem processadas: {len(estruturas_data)} registros")

            for estrutura in estruturas_data:
                caminho = estrutura.caminho_completo
                nomepasta = estrutura.nomepasta

                # Obter todos os registros acima na hierarquia para substituir os placeholders
                caminho_final = caminho
                parent_ids = []
                parent_nomes = {}

                estrutura_atual_id = estrutura.id
                empresa_id = estrutura.empresa_id

                # Montar o dicionário de substituições
                substituicoes = {}

                # Obter registros da hierarquia
                query = select(empresas_estruturas).where(
                    and_(
                        empresas_estruturas.c.empresa_id == empresa_id,
                        empresas_estruturas.c.id <= estrutura_atual_id  # Pressupõe que IDs aumentam na hierarquia
                    )
                ).order_by(empresas_estruturas.c.nivel)
                hierarquia = session.execute(query).fetchall()

                for h in hierarquia:
                    if 'AutoPastaWebot - ANO' in h.caminho_completo:
                        substituicoes['AutoPastaWebot - ANO'] = h.nomepasta
                    if 'AutoPastaWebot - MÊS' in h.caminho_completo:
                        substituicoes['AutoPastaWebot - MÊS'] = h.nomepasta

                # Substituir os placeholders
                caminho_final = substituir_placeholders(caminho, substituicoes)

                # Criar a pasta se não existir
                criar_pasta_se_nao_existir(caminho_final)

                # Ajustar permissões
                ajustar_permissoes(engine, caminho_final, estrutura.estrutura_id)
                garantir_heranca(caminho_final)

                # Atualizar status 'gerado' para 'S'
                stmt = update(empresas_estruturas).where(empresas_estruturas.c.id == estrutura.id).values(gerado='S')
                session.execute(stmt)

            session.commit()
    except SQLAlchemyError as e:
        #print(f"Erro ao criar estrutura de pastas: {e}")
        session.rollback()

# Chamada principal do script
if __name__ == "__main__":
    # Carregar os dados das tabelas
    estruturas_data, pastas_data, empresas_data, empresas_estruturas, permissoes_data, tipos_permissao_data, grupos_data = carregar_dados()

    # Preencher a tabela de hierarquia de pastas por empresa
    preencher_tabela_empresas_estruturas(empresas_data, estruturas_data, pastas_data)

    # Criar a estrutura de pastas para a empresa 7472
    print("### Criação das Pastas ###")
    criar_estrutura_pastas()

    print("Estrutura de pastas criada com sucesso.END")
