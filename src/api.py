from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, MetaData, Table, select, update
from typing import List, Optional
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from pathlib import Path

app = FastAPI()

# Carrega o .env que está um nível acima de src/
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

DATABASE_URI = os.getenv("DATABASE_URI")
if not DATABASE_URI:
    raise ValueError("DATABASE_URI não definida nas variáveis de ambiente.")

# Configuração da conexão com o banco de dados

engine = create_engine(DATABASE_URI, echo=False)
metadata = MetaData()

# Reflete as tabelas existentes no banco de dados
Estruturas = Table("WeBotPastasEstruturas", metadata, autoload_with=engine)
Pastas = Table("WeBotPastasPastas", metadata, autoload_with=engine)
Permissoes = Table("WeBotPastasPermissoes", metadata, autoload_with=engine)

# Novas tabelas para consulta
Grupos = Table("WeBotPastasgrupos", metadata, autoload_with=engine)
TiposPermissao = Table("WeBotPastastipos_permissao", metadata, autoload_with=engine)

# >>> Adicionando reflexão da tabela WeBotPastasEmpresas
Empresas = Table("WeBotPastasEmpresas", metadata, autoload_with=engine)

# Modelos Pydantic existentes

# Modelo para árvore de pastas
class FolderNode(BaseModel):
    id: int
    pai_id: Optional[int]
    nomepasta: str
    children: List["FolderNode"] = []

    class Config:
        orm_mode = True

FolderNode.model_rebuild()

# Modelo para mapeamento de permissões
class PermissionMapping(BaseModel):
    grupo_ids: List[int]
    permissao_id: int

# Modelo para criação conjunta de Estrutura e Permissões
class EstruturaPermissaoCreate(BaseModel):
    WeBotPastas_pasta_id: int
    auto: Optional[str] = None
    gerado: Optional[str] = None
    pai_id: Optional[int] = None
    replicar_para_empresas: Optional[bool] = False
    permissoes: List[PermissionMapping]

# Endpoints já implementados

@app.get("/arvore", response_model=List[FolderNode])
def get_arvore():
    with engine.connect() as conn:
        stmt = select(
            Estruturas.c.id,
            Estruturas.c.pai_id,
            Pastas.c.nomepasta
        ).select_from(
            Estruturas.join(Pastas, Estruturas.c.WeBotPastas_pasta_id == Pastas.c.id)
        )
        result = conn.execute(stmt).fetchall()

    nodes = {}
    for row in result:
        nodes[row.id] = {
            "id": row.id,
            "pai_id": row.pai_id,
            "nomepasta": row.nomepasta,
            "children": []
        }
    tree = []
    for node in nodes.values():
        if node["pai_id"] is None:
            tree.append(node)
        else:
            parent = nodes.get(node["pai_id"])
            if parent:
                parent["children"].append(node)
            else:
                tree.append(node)
    return tree

@app.post("/estrutura-permissao", status_code=201)
def create_estrutura_permissao(data: EstruturaPermissaoCreate):
    try:
        with engine.begin() as conn:
            # Inserir a nova estrutura
            stmt_estruturas = Estruturas.insert().values(
                WeBotPastas_pasta_id=data.WeBotPastas_pasta_id,
                auto=data.auto,
                gerado=data.gerado,
                pai_id=data.pai_id,
                replicar_para_empresas=1 if data.replicar_para_empresas else 0
            )
            result = conn.execute(stmt_estruturas)
            estrutura_id = result.inserted_primary_key[0]

            # Inserir permissões associadas
            for mapping in data.permissoes:
                for grupo in mapping.grupo_ids:
                    stmt_permissoes = Permissoes.insert().values(
                        estrutura_id=estrutura_id,
                        grupo_id=grupo,
                        permissao_id=mapping.permissao_id
                    )
                    conn.execute(stmt_permissoes)

            # >>> Atualizar a tabela WeBotPastasEmpresas se auto == 'S'
            if data.auto == 'S':
                stmt_update_empresas = update(Empresas).values(gerado='N')
                conn.execute(stmt_update_empresas)

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao criar registros: {e}")
    
    return {"estrutura_id": estrutura_id}


# Endpoints para consulta simples

class Grupo(BaseModel):
    id: int
    nome: Optional[str] = None

    class Config:
        orm_mode = True

class PastaItem(BaseModel):
    id: int
    nomepasta: str

    class Config:
        orm_mode = True

class TipoPermissao(BaseModel):
    id: int
    nome: Optional[str] = None

    class Config:
        orm_mode = True

@app.get("/grupos", response_model=List[Grupo])
def get_grupos():
    with engine.connect() as conn:
        stmt = select(Grupos)
        result = conn.execute(stmt).fetchall()
    return result

@app.get("/pastas", response_model=List[PastaItem])
def get_pastas():
    with engine.connect() as conn:
        stmt = select(Pastas)
        result = conn.execute(stmt).fetchall()
    return result

@app.get("/tipos-permissao", response_model=List[TipoPermissao])
def get_tipos_permissao():
    with engine.connect() as conn:
        stmt = select(TiposPermissao)
        result = conn.execute(stmt).fetchall()
    return result

# --- NOVA FUNCIONALIDADE: Inclusão de uma nova pasta ---

# Novo modelo para criação de pastas
class PastaCreate(BaseModel):
    nomepasta: str

    class Config:
        orm_mode = True

@app.post("/pastas", response_model=PastaItem, status_code=201)
def create_pasta(data: PastaCreate):
    """
    Insere um novo registro na tabela WeBotPastasPastas.
    """
    try:
        with engine.begin() as conn:
            stmt = Pastas.insert().values(nomepasta=data.nomepasta)
            result = conn.execute(stmt)
            pasta_id = result.inserted_primary_key[0]
            # Seleciona o registro recém-criado para retorno
            stmt_select = select(Pastas).where(Pastas.c.id == pasta_id)
            new_pasta = conn.execute(stmt_select).fetchone()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao criar a pasta: {e}")
    return new_pasta
