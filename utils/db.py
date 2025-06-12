# utils/db.py
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Cargar variables de entorno del archivo .env
load_dotenv()

# Obtener la URL de la base de datos de las variables de entorno
DATABASE_URL = os.getenv("DATABASE_URL")

# Verificar si la URL de la base de datos está configurada
if not DATABASE_URL:
    raise ValueError("DATABASE_URL no está configurada en el archivo .env o en el entorno.")

# Crear el motor de la base de datos de SQLAlchemy
# echo=True mostrará las consultas SQL en la consola (útil para depurar)
engine = create_engine(DATABASE_URL, echo=False) # Cambia a True si quieres ver las queries SQL

# Configurar la sesión de la base de datos
# autocommit=False: no se guardan los cambios automáticamente
# autoflush=False: no se vacían las operaciones automáticamente
# bind=engine: vincula la sesión al motor de la base de datos
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Crear una base declarativa para los modelos de SQLAlchemy
# Esta base será usada por tus clases de modelo (Equipo, Jugador)
Base = declarative_base()

# Función de dependencia para obtener una sesión de base de datos
# FastAPI usa esta función para inyectar una sesión de DB en tus rutas
def get_db():
    db = SessionLocal() # Crea una nueva sesión
    try:
        yield db # Proporciona la sesión de la base de datos al consumidor
    finally:
        db.close() # Asegura que la sesión se cierre después de su uso
