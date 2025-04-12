import pandas as pd
from sqlalchemy import create_engine, Table, MetaData, insert
from sqlalchemy.exc import SQLAlchemyError

# Configuração da conexão com o banco de dados
DATABASE_URI = 'mysql+pymysql://Hugo_Full:pA8FQ!11[?@54.232.17.99:3306/AxioDataBase'
engine = create_engine(DATABASE_URI, echo=False)

# Carregar os dados da planilha
file_path = r'D:\WeBot -Arquivo Digital\ESTRUTURA DE ACESSO.xlsx'
access_structure_df = pd.read_excel(file_path, sheet_name='ESTRUTURA DE ACESSO')

# Filtrar as linhas onde a coluna 'PERMISSÕES' é igual a 'N'
filtered_df = access_structure_df[access_structure_df['PERMISSÕES'] == 'N']

# Listas de grupos e permissões
grupos = {
    "Admins. do domínio": 1,
    "GRUPO\\Arquivo Digital - Diretoria": 2,
    "GRUPO\\Arquivo Digital - Arquivo": 3,
    "GRUPO\\Arquivo Digital - Comercial Colaboradores": 4,
    "GRUPO\\Arquivo Digital - Comercial Facilitadores": 5,
    "GRUPO\\Arquivo Digital - Contabil Colaboradores": 6,
    "GRUPO\\Arquivo Digital - Contabil Facilitadores": 7,
    "GRUPO\\Arquivo Digital - Equipe Apoio Técnico Comercial": 8,
    "GRUPO\\Arquivo Digital - Expediente Colaboradores": 9,
    "GRUPO\\Arquivo Digital - Expediente Facitadores": 10,
    "GRUPO\\Arquivo Digital - Financeiro Colaboradores": 11,
    "GRUPO\\Arquivo Digital - Financeiro Facilitadores": 12,
    "GRUPO\\Arquivo Digital - Fiscal Colaboradores": 13,
    "GRUPO\\Arquivo Digital - Fiscal Facilitadores": 14,
    "GRUPO\\Arquivo Digital - Imposto de Renda Colaboradores": 15,
    "GRUPO\\Arquivo Digital - Imposto de Renda Facilitadores": 16,
    "GRUPO\\Arquivo Digital - Legal Colaboradores": 17,
    "GRUPO\\Arquivo Digital - Legal Facilitadores": 18,
    "GRUPO\\Arquivo Digital - Marketing Colaboradores": 19,
    "GRUPO\\Arquivo Digital - Marketing Facilitadores": 20,
    "GRUPO\\Arquivo Digital - MWS Colaboradores": 21,
    "GRUPO\\Arquivo Digital - MWS Facilitadores": 22,
    "GRUPO\\Arquivo Digital - Pessoal Colaboradores": 23,
    "GRUPO\\Arquivo Digital - Pessoal Facilitadores": 24,
    "GRUPO\\Arquivo Digital - Recepção Colaboradores": 25,
    "GRUPO\\Arquivo Digital - Recepção Facilitadores": 26,
    "GRUPO\\Arquivo Digital - Recursos Humanos Colaboradores": 27,
    "GRUPO\\Arquivo Digital - Recursos Humanos Facilitadores": 28,
    "GRUPO\\Arquivo Digital - Reinf Colaboradores": 29,
    "GRUPO\\Arquivo Digital - Reinf Facilitadores": 30,
    "GRUPO\\Arquivo Digital - Tributos Colaboradores": 31,
    "GRUPO\\Arquivo Digital - Tributos Facilitadores": 32,
    "GRUPO\\Arquivo Digital - Sucesso do Cliente Colaboradores": 33,
    "GRUPO\\Arquivo Digital - Sucesso do Cliente Facilitadores": 34,
    "RenatoS": 35
}

permissoes = {
    "Modify": 1,
    "ReadAndExecute": 2,
    "FullControl": 3
}

# Função para obter o ID de um grupo baseado no nome
def get_grupo_id(grupo_nome):
    return grupos.get(grupo_nome, None)

# Função para obter o ID de uma permissão baseada no nome
def get_permissao_id(permissao_nome):
    return permissoes.get(permissao_nome, None)

# Inserir permissões no banco de dados
def inserir_permissoes(conn, estrutura_id, grupo_id, permissao_id):
    meta = MetaData()
    permissoes = Table('WeBotPastasPermissoes', meta, autoload_with=conn)
    
    try:
        ins = permissoes.insert().values(
            estrutura_id=estrutura_id,
            grupo_id=grupo_id,
            permissao_id=permissao_id
        )
        conn.execute(ins)
        print(f"Permissão inserida: Estrutura ID {estrutura_id}, Grupo ID {grupo_id}, Permissão ID {permissao_id}")
    except SQLAlchemyError as e:
        print(f"Erro ao inserir permissão: {e}")

# Mapear as permissões da planilha para os IDs do banco de dados e inserir
with engine.connect() as conn:
    trans = conn.begin()  # Iniciar a transação
    try:
        for idx, row in filtered_df.iterrows():
            print(f"Processando linha {idx + 1}...")
            estrutura_id = row['WeBotPastasEstruturas_id']
            
            if pd.notna(estrutura_id):
                print(f"Estrutura ID: {estrutura_id}")
                grupos_processados = set()
                for col in filtered_df.columns[12:80]:  # Colunas de permissões (J até BU)
                    if pd.notna(row[col]) and row[col] == 'X':
                        try:
                            grupo_nome, permissao_nome = col.rsplit(' - ', 1)
                            grupo_nome = grupo_nome.strip()
                            permissao_nome = permissao_nome.strip()
                            
                            print(f"Grupo: {grupo_nome}, Permissão: {permissao_nome}")
                            
                            if permissao_nome == 'ReadAndExecute' and f'{grupo_nome} - Modify' in filtered_df.columns and row[f'{grupo_nome} - Modify'] == 'X':
                                print(f"Ignorando ReadAndExecute para {grupo_nome} porque Modify está definido.")
                                continue
                            
                            if grupo_nome not in grupos_processados or permissao_nome != 'ReadAndExecute':
                                grupo_id = get_grupo_id(grupo_nome)
                                permissao_id = get_permissao_id(permissao_nome)
                                
                                if grupo_id and permissao_id:
                                    inserir_permissoes(conn, estrutura_id, grupo_id, permissao_id)
                                    grupos_processados.add(grupo_nome)
                        except ValueError:
                            print(f"Erro ao processar a coluna: {col}")

                # Garantir que Admins. do domínio e RenatoS tenham FullControl
                for grupo_especial in ['Admins. do domínio', 'RenatoS']:
                    grupo_id = get_grupo_id(grupo_especial)
                    permissao_id = get_permissao_id('FullControl')
                    if grupo_id and permissao_id:
                        inserir_permissoes(conn, estrutura_id, grupo_id, permissao_id)
                    else:
                        print(f"Erro ao processar grupo especial: {grupo_especial}")

        trans.commit()  # Confirmar a transação
    except Exception as e:
        trans.rollback()  # Reverter a transação em caso de erro
        print(f"Erro ao processar permissões: {e}")

print("Processamento de permissões concluído.")
