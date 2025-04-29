# src/create_db.py

from sqlalchemy import create_engine
from pathlib import Path
from dotenv import load_dotenv
import os

# Carrega o .env que está um nível acima de src/
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

DATABASE_URI = os.getenv("DATABASE_URI")
if not DATABASE_URI:
    raise ValueError("DATABASE_URI não definida nas variáveis de ambiente.")

# Importa os modelos e o Base
from src.models import Base  # Certifique-se que Base está definido no models.py

# Cria a engine e aplica os modelos
engine = create_engine(DATABASE_URI)

# Cria todas as tabelas declaradas nos modelos
Base.metadata.create_all(engine)

print("✅ Banco de dados criado com sucesso a partir dos modelos.")
