from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError, OperationalError
from data import models
from data.models import MascotaCreate, MascotaUpdate
from typing import Optional

# --- Operaciones CRUD para Macotas ---

def create_mascota(db: Session, mascota: MascotaCreate):
    try:
        imagen_url_str = str(mascota.imagen_url) if mascota.imagen_url else None

        db_mascota = models.Mascota(
            nombre=mascota.nombre,
            pais=mascota.pais,
            grupo=mascota.grupo,
            imagen_url=imagen_url_str
        )
        db.add(db_mascota)
        db.commit()
        db.refresh(db_mascota)
        return db_mascota
    except IntegrityError as e:
        db.rollback()
        print(f"¡Error de integridad al crear el mascota! Detalles: {e}")
        raise ValueError("Ya existe una mascota con ese nombre o datos inválidos.")
    except Exception as e:
        db.rollback()
        print(f"¡Oops! Un error inesperado ocurrió al crear la mascota: {e}")
        raise

def get_all_mascotas(db: Session, skip: int = 0, limit: int = 100):
    try:
        return db.query(models.Mascota).options(joinedload(models.Mascota.Usuario)).filter(
            models.Mascota.eliminado_logico == False
        ).offset(skip).limit(limit).all()
    except OperationalError as e:
        print(f"¡Problema de conexión con la base de datos al obtener mascotas! Detalles: {e}")
        raise ConnectionError("No se pudo conectar a la base de datos.")
    except Exception as e:
        print(f"¡Error desconocido al obtener todas las mascotas! Detalles: {e}")
        raise

def get_mascota_by_id(db: Session, mascota_id: int):
    try:
        return db.query(models.Mascota).options(joinedload(models.Mascota.Usuario)).filter(
            models.Mascota.id == mascota_id
        ).first()
    except OperationalError as e:
        print(f"¡Problema de conexión con la base de datos al buscar mascota por ID! Detalles: {e}")
        raise ConnectionError("No se pudo conectar a la base de datos.")
    except Exception as e:
        print(f"¡Error desconocido al buscar mascota por ID {equipo_id}! Detalles: {e}")
        raise

def update_mascota(db: Session, mascota_id: int, mascota: MascotaUpdate):
    try:
        db_mascota = db.query(models.Mascota).filter(models.Mascota.id == mascota_id).first()
        if db_mascota:
            update_data = mascota.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                # Convertir HttpUrl a str si es necesario
                if key == "imagen_url" and value is not None:
                    setattr(db_mascota, key, str(value))
                else:
                    setattr(db_mascota, key, value)
            db.commit()
            db.refresh(db_mascota)
        return db_mascota
    except IntegrityError as e:
        db.rollback()
        print(f"¡Error de integridad al actualizar la mascota! Detalles: {e}")
        raise ValueError("No se pudo actualizar la mascota debido a datos inválidos o duplicados.")
    except Exception as e:
        db.rollback()
        print(f"¡Oops! Un error inesperado ocurrió al actualizar la mascota con ID {mascota_id}: {e}")
        raise

def soft_delete_mascota(db: Session, mascota_id: int):
    try:
        db_mascota = db.query(models.Mascota).filter(models.Mascota.id == mascota_id).first()
        if db_mascota:
            db_mascota.eliminado_logico = True
            db.commit()
            db.refresh(db_mascota)
        return db_mascota
    except OperationalError as e:
        db.rollback()
        print(f"¡Problema de conexión con la base de datos al eliminar mascota {mascota_id}! Detalles: {e}")
        raise ConnectionError("No se pudo conectar a la base de datos para eliminar la mascota.")
    except Exception as e:
        db.rollback()
        print(f"¡Error desconocido al intentar eliminar lógicamente la mascota con ID {equipo_id}! Detalles: {e}")
        raise

def search_mascotas(
    db: Session,
    nombre: Optional[str] = None,
    tipo: Optional[str] = None,
    raza: Optional[str] = None,
    id_usuario: Optional[int] = None, # Renombrado para mayor claridad
    id_vuelo: Optional[int] = None,
    eliminado: bool = False,
):
    try:
        query = db.query(models.Mascota).filter(models.Mascota.eliminado_logico == eliminado)
        if nombre:
            # Buscar por nombre (case-insensitive)
            query = query.filter(models.Mascota.nombre.ilike(f"%{nombre}%"))
        if tipo:
            query = query.filter(models.Mascota.tipo.ilike(f"%{tipo}%"))
        if raza:
            query = query.filter(models.Mascota.raza.ilike(f"%{raza}%"))
        if id_mascota:
            query = query.filter(models.Mascota.id == id_mascota)

        return query.all()
    except OperationalError as e:
        print(f"¡Problema de conexión con la base de datos al buscar mascotas! Detalles: {e}")
        raise ConnectionError("No se pudo conectar a la base de datos para realizar la búsqueda.")
    except Exception as e:
        print(f"¡Error desconocido al buscar mascotas! Detalles: {e}")
        raise

def get_soft_deleted_mascotas(db: Session, skip: int = 0, limit: int = 100):
    try:
        return db.query(models.Mascota).filter(
            models.Mascota.eliminado_logico == True
        ).offset(skip).limit(limit).all()
    except OperationalError as e:
        print(f"¡Problema de conexión con la base de datos al obtener mascotas eliminadas! Detalles: {e}")
        raise ConnectionError("No se pudo conectar a la base de datos para obtener equipos eliminados.")
    except Exception as e:
        print(f"¡Error desconocido al obtener mascotas eliminadas lógicamente! Detalles: {e}")
        raise