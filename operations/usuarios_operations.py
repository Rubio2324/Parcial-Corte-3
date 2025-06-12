from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError, OperationalError
from data import models
from data.models import UsuarioCreate, UsuarioUpdate
from typing import Optional

# --- Operaciones CRUD para Macotas ---

def create_Usuario(db: Session, Usuario: UsuarioCreate):
    try:
        imagen_url_str = str(Usuario.imagen_url) if Usuario.imagen_url else None

        db_Usuario = models.Mascota(
            nombre=Usuario.nombre,
            mascota_id=Usuario.mascota_id,
            vuelo_id=Usuario.vuelo_id,
            nacionalidad=Usuario.nacionalidad,
            imagen_url=imagen_url_str
        )
        db.add(db_Usuario)
        db.commit()
        db.refresh(db_Usuario)
        return db_Usuario
    except IntegrityError as e:
        db.rollback()
        print(f"¡Error de integridad al crear el Usuario! Detalles: {e}")
        raise ValueError("Ya existe una Usuario con ese nombre o datos inválidos.")
    except Exception as e:
        db.rollback()
        print(f"¡Oops! Un error inesperado ocurrió al crear el Usuario: {e}")
        raise

def get_all_Usuario(db: Session, skip: int = 0, limit: int = 100):
    try:
        return db.query(models.Mascota).options(joinedload(models.Usuario.Usuario)).filter(
            models.Usuario.eliminado_logico == False
        ).offset(skip).limit(limit).all()
    except OperationalError as e:
        print(f"¡Problema de conexión con la base de datos al obtener Usuarios! Detalles: {e}")
        raise ConnectionError("No se pudo conectar a la base de datos.")
    except Exception as e:
        print(f"¡Error desconocido al obtener todas los Usuarios! Detalles: {e}")
        raise

def get_Usuario_by_id(db: Session, Usuario_id: int):
    try:
        return db.query(models.Usuario).options(joinedload(models.Usuario.Usuario)).filter(
            models.Usuario.id == Usuario_id
        ).first()
    except OperationalError as e:
        print(f"¡Problema de conexión con la base de datos al buscar el Usuario por ID! Detalles: {e}")
        raise ConnectionError("No se pudo conectar a la base de datos.")
    except Exception as e:
        print(f"¡Error desconocido al buscar Usuario por ID {Usuario_id}! Detalles: {e}")
        raise

def update_Usuario(db: Session, Usuario_id: int, Usuario: UsuarioUpdate):
    try:
        db_Usuario = db.query(models.Usuario).filter(models.Usuario.id == Usuario_id).first()
        if db_Usuario:
            update_data = Usuario.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                # Convertir HttpUrl a str si es necesario
                if key == "imagen_url" and value is not None:
                    setattr(db_Usuario,key, str(value))
                else:
                    setattr(db_Usuario, key, value)
            db.commit()
            db.refresh(db_Usuario)
        return db_Usuario
    except IntegrityError as e:
        db.rollback()
        print(f"¡Error de integridad al actualizar el Usuario! Detalles: {e}")
        raise ValueError("No se pudo actualizar el Usuario debido a datos inválidos o duplicados.")
    except Exception as e:
        db.rollback()
        print(f"¡Oops! Un error inesperado ocurrió al actualizar el Usuario con ID {Usuario_id}: {e}")
        raise

def soft_delete_Usuario(db: Session, Usuario_id: int):
    try:
        db_Usuario = db.query(models.Usuario).filter(models.Usuario.id == Usuario_id).first()
        if db_Usuario:
            db_Usuario.eliminado_logico = True
            db.commit()
            db.refresh(db_Usuario)
        return db_Usuario
    except OperationalError as e:
        db.rollback()
        print(f"¡Problema de conexión con la base de datos al eliminar Usuario {Usuario_id}! Detalles: {e}")
        raise ConnectionError("No se pudo conectar a la base de datos para eliminar la Usuario.")
    except Exception as e:
        db.rollback()
        print(f"¡Error desconocido al intentar eliminar lógicamente la Usuario con ID {Usuario_id}! Detalles: {e}")
        raise

def search_Usuario(
    db: Session,
    nombre:Optional[str]= None,
    mascota_id: Optional[int] = None,
    vuelo_id: Optional[int] = None,
    nacionalidad: Optional[str] = None,
    id_usuario: Optional[int] = None, # Renombrado para mayor claridad
    id_vuelo: Optional[int] = None,
    eliminado: bool = False,
):
    try:
        query = db.query(models.Mascota).filter(models.Usuario.eliminado_logico == eliminado)
        if nombre:
            # Buscar por nombre (case-insensitive)
            query = query.filter(models.Usuario.nombre.ilike(f"%{nombre}%"))
        if mascota_id:
            query = query.filter(models.Usuario.tipo.ilike(f"%{mascota_id}%"))
        if vuelo_id:
            query = query.filter(models.Usuario.raza.ilike(f"%{vuelo_id}%"))
        if nacionalidad:
            query = query.filter(models.Usuario.id == nacionalidad)

        return query.all()
    except OperationalError as e:
        print(f"¡Problema de conexión con la base de datos al buscar Usuario! Detalles: {e}")
        raise ConnectionError("No se pudo conectar a la base de datos para realizar la búsqueda.")
    except Exception as e:
        print(f"¡Error desconocido al buscar Usuarios! Detalles: {e}")
        raise

def get_soft_deleted_Usuario(db: Session, skip: int = 0, limit: int = 100):
    try:
        return db.query(models.Usuario).filter(
            models.Usuario.eliminado_logico == True
        ).offset(skip).limit(limit).all()
    except OperationalError as e:
        print(f"¡Problema de conexión con la base de datos al obtener Usuario eliminadas! Detalles: {e}")
        raise ConnectionError("No se pudo conectar a la base de datos para obtener equipos Usuario.")
    except Exception as e:
        print(f"¡Error desconocido al obtener mascotas eliminadas lógicamente! Detalles: {e}")
        raise