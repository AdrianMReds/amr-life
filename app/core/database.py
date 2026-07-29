# app/core/database.py
import os
from contextlib import contextmanager
# pyrefly: ignore [missing-import]
from psycopg_pool import ConnectionPool

from dotenv import load_dotenv

load_dotenv()

# 1. Obtener la cadena de conexión de Neon (preferiblemente usando pooling de Neon, la que tiene -pooler)
DATABASE_URL = os.getenv("DATABASE_URL")

# 2. Inicializar el Pool global. 
# min_size=1 mantiene al menos una conexión viva. max_size ajusta según tus necesidades.
pool = ConnectionPool(
    conninfo=DATABASE_URL,
    min_size=1,
    max_size=10,
    kwargs={"autocommit": True} # Recomendado para queries directos, puedes manejar transacciones manualmente si cambias a False
)

@contextmanager
def get_db_client():
    """
    Context Manager para proveer una conexión del pool a cualquier archivo.
    Garantiza que la conexión se devuelva al pool al terminar, incluso si hay errores.
    """
    with pool.connection() as conn:
        with conn.cursor() as cur:
            yield cur
            # Al salir del bloque 'with', el cursor y la conexión se liberan automáticamente