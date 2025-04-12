# api.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Boolean, insert
from sqlalchemy.exc import SQLAlchemyError

app = FastAPI()

# Configuração da conexão com o banco de dados
DATABASE_URI = 'mysql+pymysql://Hugo_Full:pA8FQ!11[?@54.232.17.99:3306/AxioDataBase'
engine = create_engine(DATABASE_URI, echo=True)
meta = MetaData()

# Refletindo as tabelas já existentes no banco
weBotPastasEstruturas = Table(
    "WeBotPastasEstruturas", meta,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("WeBotPastas_pasta_id", Integer),
    Column("auto", String(10)),
    Column("gerado", String(10)),
    Column("pai_id", Integer),
    Column("replicar_para_empresas", Boolean),
    autoload_with=engine
)

weBotPastasPermissoes = Table(
    "WeBotPastasPermissoes", meta,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("estrutura_id", Integer),
    Column("grupo_id", Integer),
    Column("permissao_id", Integer),
    autoload_with=engine
)

# Modelos para entrada de dados
class PermissaoInput(BaseModel):
    grupo: str
    permissao: str

class EstruturaInput(BaseModel):
    WeBotPastas_pasta_id: Optional[int] = None
    auto: Optional[str] = None
    gerado: Optional[str] = None
    pai_id: Optional[int] = None
    replicar_para_empresas: Optional[bool] = False
    permissoes: List[PermissaoInput]

# Dicionários para mapear nomes de grupos e permissões para seus respectivos IDs
# Esses valores podem vir de uma consulta a uma tabela ou serem configurados de outra forma
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

permissoes_dict = {
    "Modify": 1,
    "ReadAndExecute": 2,
    "FullControl": 3
}

@app.post("/estruturas")
def criar_estrutura(estrutura: EstruturaInput):
    with engine.connect() as conn:
        trans = conn.begin()
        try:
            # Inserir a estrutura (pasta) no banco
            ins = weBotPastasEstruturas.insert().values(
                WeBotPastas_pasta_id=estrutura.WeBotPastas_pasta_id,
                auto=estrutura.auto,
                gerado=estrutura.gerado,
                pai_id=estrutura.pai_id,
                replicar_para_empresas=estrutura.replicar_para_empresas,
            )
            result = conn.execute(ins)
            estrutura_id = result.inserted_primary_key[0]

            # Inserir cada permissão associada à estrutura
            for perm in estrutura.permissoes:
                grupo_id = grupos.get(perm.grupo)
                permissao_id = permissoes_dict.get(perm.permissao)
                if not grupo_id or not permissao_id:
                    trans.rollback()
                    raise HTTPException(status_code=400, detail=f"Grupo ou Permissão inválidos: {perm}")
                ins_perm = weBotPastasPermissoes.insert().values(
                    estrutura_id=estrutura_id,
                    grupo_id=grupo_id,
                    permissao_id=permissao_id
                )
                conn.execute(ins_perm)

            trans.commit()
            return {"status": "sucesso", "estrutura_id": estrutura_id}
        except SQLAlchemyError as e:
            trans.rollback()
            raise HTTPException(status_code=500, detail=f"Erro ao inserir dados: {e}")
