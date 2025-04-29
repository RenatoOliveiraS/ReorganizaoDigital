import os
import logging
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from pathlib import Path


# Conexão com banco de execuções
def conectar_banco_execucoes():
    # Carrega o .env que está um nível acima de src/
    env_path = Path(__file__).parent.parent / '.env'
    load_dotenv(dotenv_path=env_path)

    DATABASE_URI = os.getenv("DATABASE_URI")
    if not DATABASE_URI:
        raise ValueError("DATABASE_URI não definida nas variáveis de ambiente.")
    return create_engine(DATABASE_URI)

def renomear_pastas():
    engine = conectar_banco_execucoes()
    with engine.begin() as conn:
        registros = conn.execute(text("""
            SELECT id,
                   empresa_id,
                   old_path,
                   caminho_completo
              FROM WeBotPastasEmpresasEstruturas
             WHERE razao_social_atualizar = 'S'
        """))
        for r in registros:
            struct_id    = r.id
            empresa_id   = r.empresa_id
            old_path     = r.old_path
            new_path     = r.caminho_completo

            if not old_path:
                logging.warning(f"[Estrutura {struct_id}] old_path vazio; pulando.")
                continue

            if not os.path.exists(old_path):
                logging.warning(f"[Estrutura {struct_id}] pasta não encontrada: {old_path}")
                continue

            parent_dir = os.path.dirname(new_path)
            if not os.path.exists(parent_dir):
                try:
                    os.makedirs(parent_dir, exist_ok=True)
                    logging.info(f"[Estrutura {struct_id}] criado diretório pai: {parent_dir}")
                except Exception as e:
                    logging.error(f"[Estrutura {struct_id}] falha ao criar {parent_dir}: {e}")
                    continue

            if os.path.exists(new_path):
                logging.info(f"[Estrutura {struct_id}] destino já existe: {new_path}")
                _marcar_como_atualizado(conn, struct_id, empresa_id)
                continue

            # renomeia de verdade
            try:
                os.rename(old_path, new_path)
                logging.info(f"[Estrutura {struct_id}] renomeado: '{old_path}' → '{new_path}'")
            except Exception as e:
                logging.error(f"[Estrutura {struct_id}] erro ao renomear: {e}")
                continue

            # atualiza banco nas duas tabelas
            _marcar_como_atualizado(conn, struct_id, empresa_id)

def _marcar_como_atualizado(conn, struct_id, empresa_id):
    # atualiza tabela de estruturas
    try:
        conn.execute(text("""
            UPDATE WeBotPastasEmpresasEstruturas
               SET old_path = NULL,
                   razao_social_atualizar = 'N'
             WHERE id = :struct_id
        """), {"struct_id": struct_id})
        logging.info(f"[Estrutura {struct_id}] marcado como atualizado em Estruturas.")
    except Exception as e:
        logging.error(f"[Estrutura {struct_id}] falha ao atualizar Estruturas: {e}")

    # atualiza tabela principal de empresas
    try:
        conn.execute(text("""
            UPDATE WeBotPastasEmpresas
               SET razao_social_atualizar = 'N'
             WHERE id = :empresa_id
        """), {"empresa_id": empresa_id})
        logging.info(f"[Empresa {empresa_id}] marcado como atualizado em Empresas.")
    except Exception as e:
        logging.error(f"[Empresa {empresa_id}] falha ao atualizar Empresas: {e}")

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s: %(message)s"
    )
    renomear_pastas()
