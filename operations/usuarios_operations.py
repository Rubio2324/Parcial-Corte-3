from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError, OperationalError
from data import models
from data.models import UsuarioCreate, UsuarioUpdate
from typing import Optional

# --- Operaciones CRUD para usuarios ---

def create_usuario(db: Session, Usuario: UsuarioCreate):
    try:
        db_usuario = models.Usuario(
            nombre=Usuario.nombre,
            edad=Usuario.edad,
            nacionalidad=Usuario.nacionalidad,
        )
        db.add(db_usuario)
        db.commit()
        db.refresh(db_usuario)
        return db_usuario
    except IntegrityError as e:
        db.rollback()
        print(f"¡Error de integridad al crear el Usuario! Detalles: {e}")
        raise ValueError("Ya existe una Usuario con ese nombre o datos inválidos.")
    except Exception as e:
        db.rollback()
        print(f"¡Oops! Un error inesperado ocurrió al crear el Usuario: {e}")
        raise

def get_all_usuario(db: Session, skip: int = 0, limit: int = 100):
    try:
        return db.query(models.Usuario).options(joinedload(models.Usuario.Mascota)).filter(
            models.Usuario.eliminado_logico == False
        ).offset(skip).limit(limit).all()
    except OperationalError as e:
        print(f"¡Problema de conexión con la base de datos al obtener Usuarios! Detalles: {e}")
        raise ConnectionError("No se pudo conectar a la base de datos.")
    except Exception as e:
        print(f"¡Error desconocido al obtener todas los Usuarios! Detalles: {e}")
        raise

def get_usuario_by_id(db: Session, id_usuario: int):
    try:
        return db.query(models.Usuario).options(joinedload(models.Usuario.Mascota)).filter(
            models.Usuario.id == id_usuario
        ).first()
    except OperationalError as e:
        print(f"¡Problema de conexión con la base de datos al buscar el Usuario por ID! Detalles: {e}")
        raise ConnectionError("No se pudo conectar a la base de datos.")
    except Exception as e:
        print(f"¡Error desconocido al buscar Usuario por ID {id_usuario}! Detalles: {e}")
        raise

def update_usuario(db: Session, id_usuario: int, Usuario: UsuarioUpdate):
    try:
        db_usuario = db.query(models.Usuario).filter(models.Usuario.id == id_usuario).first()
        if db_usuario:
            update_data = Usuario.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_usuario, key, value)
            db.commit()
            db.refresh(db_usuario)
        return db_usuario
    except IntegrityError as e:
        db.rollback()
        print(f"¡Error de integridad al actualizar el Usuario! Detalles: {e}")
        raise ValueError("No se pudo actualizar el Usuario debido a datos inválidos o duplicados.")
    except Exception as e:
        db.rollback()
        print(f"¡Oops! Un error inesperado ocurrió al actualizar el Usuario con ID {id_usuario}: {e}")
        raise

def soft_delete_usuario(db: Session, id_usuario: int):
    try:
        db_usuario = db.query(models.Usuario).filter(models.Usuario.id == id_usuario).first()
        if db_usuario:
            db_usuario.eliminado_logico = True
            db.commit()
            db.refresh(db_usuario)
        return db_usuario
    except OperationalError as e:
        db.rollback()
        print(f"¡Problema de conexión con la base de datos al eliminar Usuario {id_usuario}! Detalles: {e}")
        raise ConnectionError("No se pudo conectar a la base de datos para eliminar la Usuario.")
    except Exception as e:
        db.rollback()
        print(f"¡Error desconocido al intentar eliminar lógicamente la Usuario con ID {id_usuario}! Detalles: {e}")
        raise

def search_usuario(
    db: Session,
    nombre:Optional[str]= None,
    nacionalidad: Optional[str] = None,
    edad: Optional[int] = None,
    id_usuario: Optional[int] = None, # Renombrado para mayor claridad
    eliminado: bool = False,
):
    try:
        query = db.query(models.Usuario).filter(models.Usuario.eliminado_logico == eliminado)
        if nombre:
            query = query.filter(models.Usuario.nombre.ilike(f"%{nombre}%"))
        if nacionalidad:
            query = query.filter(models.Usuario.nacionalidad.ilike(f"%{nacionalidad}%"))
        if edad:
            query = query.filter(models.Usuario.edad.ilike(f"%{edad}%"))
        if id_usuario:
            query = query.filter(models.Usuario.id == id_usuario)

        return query.all()
    except OperationalError as e:
        print(f"¡Problema de conexión con la base de datos al buscar Usuario! Detalles: {e}")
        raise ConnectionError("No se pudo conectar a la base de datos para realizar la búsqueda.")
    except Exception as e:
        print(f"¡Error desconocido al buscar Usuarios! Detalles: {e}")
        raise

def get_soft_deleted_usuarios(db: Session, skip: int = 0, limit: int = 100):
    try:
        return db.query(models.Usuario).filter(
            models.Usuario.eliminado_logico == True
        ).offset(skip).limit(limit).all()
    except OperationalError as e:
        print(f"¡Problema de conexión con la base de datos al obtener usuarios eliminadas! Detalles: {e}")
        raise ConnectionError("No se pudo conectar a la base de datos para obtener usuarios eliminados.")
    except Exception as e:
        print(f"¡Error desconocido al obtener usuarios eliminadas lógicamente! Detalles: {e}")
        raise