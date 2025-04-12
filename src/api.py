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

# Modelo Pydantic para representar cada nó da árvore de pastas
class FolderNode(BaseModel):
    id: int
    pai_id: Optional[int]
    nomepasta: str
    children: List["FolderNode"] = []

    class Config:
        orm_mode = True

FolderNode.update_forward_refs()

@app.get("/arvore", response_model=List[FolderNode])
def get_arvore():
    """
    Carrega a árvore de pastas:
    - Realiza um join entre WeBotPastasEstruturas e WeBotPastasPastas
    - Constrói um dicionário com cada nó indexado por id
    - Associa cada nó ao seu pai, usando o campo pai_id
    - Retorna os nós raiz (aqueles com pai_id nulo) como árvore
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
                # Se não encontrar um pai, trata-o como nó raiz
                tree.append(node)
    return tree
