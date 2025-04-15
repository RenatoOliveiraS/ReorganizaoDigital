from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, MetaData, Table, select
from typing import List, Optional
from pydantic import BaseModel

app = FastAPI()

# Configuração da conexão com o banco de dados
DATABASE_URI = 'mysql+pymysql://Hugo_Full:pA8FQ!11[?@54.232.17.99:3306/AxioDataBase'
engine = create_engine(DATABASE_URI, echo=False)
metadata = MetaData()

# Reflete as tabelas existentes no banco de dados
Estruturas = Table("WeBotPastasEstruturas", metadata, autoload_with=engine)
Pastas = Table("WeBotPastasPastas", metadata, autoload_with=engine)
Permissoes = Table("WeBotPastasPermissoes", metadata, autoload_with=engine)

# Modelo Pydantic para representar cada nó da árvore de pastas (GET /arvore)
class FolderNode(BaseModel):
    id: int
    pai_id: Optional[int]
    nomepasta: str
    children: List["FolderNode"] = []

    class Config:
        orm_mode = True

FolderNode.model_rebuild()

# Novo modelo para representar cada mapeamento de permissão, onde pode haver vários grupo_ids para um permissao_id
class PermissionMapping(BaseModel):
    grupo_ids: List[int]
    permissao_id: int

# Novo modelo unificado para criação conjunta de Estrutura e Permissões
class EstruturaPermissaoCreate(BaseModel):
    # Dados da tabela Estruturas
    WeBotPastas_pasta_id: int
    auto: Optional[str] = None
    gerado: Optional[str] = None
    pai_id: Optional[int] = None
    replicar_para_empresas: Optional[bool] = False
    # Dados para a criação de múltiplos registros em Permissoes
    permissoes: List[PermissionMapping]

@app.get("/arvore", response_model=List[FolderNode])
def get_arvore():
    """
    Carrega a árvore de pastas:
    - Realiza um join entre WeBotPastasEstruturas e WeBotPastasPastas.
    - Constrói um dicionário com cada nó indexado por id.
    - Associa cada nó ao seu pai, usando o campo pai_id.
    - Retorna os nós raiz (aqueles com pai_id nulo) como árvore.
    """
    with engine.connect() as conn:
        stmt = select(
            Estruturas.c.id,
            Estruturas.c.pai_id,
            Pastas.c.nomepasta
        ).select_from(
            Estruturas.join(Pastas, Estruturas.c.WeBotPastas_pasta_id == Pastas.c.id)
        )
        result = conn.execute(stmt).fetchall()

    # Cria um dicionário com os nós, indexados pelo id
    nodes = {}
    for row in result:
        nodes[row.id] = {
            "id": row.id,
            "pai_id": row.pai_id,
            "nomepasta": row.nomepasta,
            "children": []
        }

    # Constrói a árvore associando cada nó ao seu pai
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
    """
    Cria, em uma única transação, um novo registro na tabela WeBotPastasEstruturas e,
    em seguida, insere os registros correspondentes na tabela WeBotPastasPermissoes.
    
    Para cada mapeamento em 'permissoes', insere um registro para cada 'grupo_id'
    associado ao 'permissao_id' informado.
    """
    try:
        # Operação transacional: ambas as inserções são realizadas de forma atômica
        with engine.begin() as conn:
            # Inserção na tabela Estruturas
            stmt_estruturas = Estruturas.insert().values(
                WeBotPastas_pasta_id=data.WeBotPastas_pasta_id,
                auto=data.auto,
                gerado=data.gerado,
                pai_id=data.pai_id,
                replicar_para_empresas=1 if data.replicar_para_empresas else 0
            )
            result = conn.execute(stmt_estruturas)
            estrutura_id = result.inserted_primary_key[0]

            # Para cada mapeamento, insere os registros na tabela Permissoes
            for mapping in data.permissoes:
                for grupo in mapping.grupo_ids:
                    stmt_permissoes = Permissoes.insert().values(
                        estrutura_id=estrutura_id,
                        grupo_id=grupo,
                        permissao_id=mapping.permissao_id
                    )
                    conn.execute(stmt_permissoes)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao criar registros: {e}")

    return {"estrutura_id": estrutura_id}
